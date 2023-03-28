"""database module contains all the database related code for the application,
such as logic for writing to the database and reading from it."""

from enum import Enum
import logging
import os
from datetime import datetime
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Load environment variables from a .env file.
load_dotenv()

# Initializes the database engine. Use env vars to pass private info.
ENGINE = create_engine(
    (
        f"mysql+mysqlconnector://"
        f"{os.getenv('DDBB_USER')}:{os.getenv('DDBB_PASSWORD')}"
        f"@{os.getenv('DDBB_HOST')}:{os.getenv('DDBB_PORT')}/main"
    ),
    echo=False,
)


class Language(str, Enum):
    """Language defines all the possible languages supported by the
    application."""

    # Spanish.
    ES = "ES"
    # English.
    EN = "EN"


class Currency(str, Enum):
    """Currency defines all the possible currencies supported by the
    application."""

    COP = "COP"
    USD = "USD"
    EUR = "EUR"


class Organization(SQLModel, table=True):
    """Represents the organization table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime
    name: str
    currency: Currency
    language: Language


class User(SQLModel, table=True):
    """Represents the user table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")
    created_at: datetime
    whatsapp_phone: str
    name: str
    is_admin: bool


class Transaction(SQLModel, table=True):
    """Represents the transaction table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime
    label: str
    value: float
    currency: str
    value_converted: float
    description: str


def record_transaction(transaction: Transaction):
    """Record a transaction to the transaction table."""

    # transaction = Transaction(
    #     created_at=created_at,
    #     user_id=user.id,
    #     label=label,
    #     value=value,
    #     currency=currency,
    #     value_converted=value_converted,
    #     description=description,
    # )
    logging.info("creating new transaction record: %s", transaction)

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(transaction)
        session.commit()

    logging.info("successfully recorded transaction")


def retrieve_transactions(
    date: datetime,
    organization: Organization,
) -> List[Transaction]:
    """Retrieve transactions from the transactions table for the given
    organization."""

    with Session(ENGINE) as session:
        # Executes statement to retrieve info from the database.
        statement = (
            select(Transaction)
            .join(User)
            .where(
                Transaction.created_at
                >= datetime(date.year, 1, 1, 0, 0, 0, 0, date.tzinfo),
                User.organization_id == organization.id,
            )
        )
        logging.info("executing sql statement: %s", statement)
        transactions = list(session.exec(statement))

    logging.info("successfully retrieved transactions")

    return transactions


def retrieve_user_organization(whatsapp_phone: str) -> Tuple[User, Organization] | None:
    """Retrieves the user and organization given the provided filter."""

    with Session(ENGINE) as session:
        statement = (
            select(User, Organization)
            .where(User.organization_id == Organization.id)
            .where(User.whatsapp_phone == whatsapp_phone)
        )
        logging.info("executing sql statement: %s", statement)
        results = session.exec(statement)
        try:
            user, organization = results.one()
            logging.info("successfully retrieved user and organization")

        except IndexError:
            logging.error(
                "no user and/or organization found for whatsapp phone %s",
                whatsapp_phone,
            )
            user, organization = None, None

    return user, organization


def retrieve_user(whatsapp_phone: str) -> User | None:
    """Retrieves the user based on the provided filter."""

    with Session(ENGINE) as session:
        statement = select(User).where(User.whatsapp_phone == whatsapp_phone)
        logging.info("executing sql statement: %s", statement)
        results = session.exec(statement)
        try:
            user = results.one()
        except IndexError:
            user = None

    return user


def retrieve_organization(user: User) -> Organization:
    """Retrieves the organization for the given user."""

    with Session(ENGINE) as session:
        statement = select(Organization).where(Organization.id == user.organization_id)
        logging.info("executing sql statement: %s", statement)
        results = session.exec(statement)
        organization = results.one()

    return organization


def record_organization(
    created_at: datetime,
    name: str,
    language: Language,
    currency: Currency,
) -> int:
    """Record an organization to the organization table. Returns the id after
    successfully recording the organization."""

    organization = Organization(
        created_at=created_at,
        name=name,
        currency=currency,
        language=language,
    )
    logging.info("creating new organization record: %s", organization)

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(organization)
        session.commit()
        session.refresh(organization)
        organization_id = organization.id

    logging.info("successfully recorded organization")

    return organization_id


def record_user(
    organization_id: int,
    created_at: datetime,
    whatsapp_phone: str,
    name: str,
    is_admin: bool,
):
    """Record a new user to the user table."""

    user = User(
        organization_id=organization_id,
        created_at=created_at,
        whatsapp_phone=whatsapp_phone,
        name=name,
        is_admin=is_admin,
    )
    logging.info("creating new user record: %s", user)

    # Stores the record in the database.
    with Session(ENGINE) as session:
        session.add(user)
        session.commit()

    logging.info("successfully recorded user")


def update_user(user: User, name: str) -> User:
    """Update a table entry for a user."""

    with Session(ENGINE) as session:
        statement = select(User).where(User.id == user.id)
        logging.info("executing sql statement: %s", statement)
        results = session.exec(statement)
        user = results.one()
        user.name = name
        session.add(user)
        session.commit()
        session.refresh(user)

    logging.info("successfully updated user")

    return user
