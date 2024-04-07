USE ROOMIO;
DROP TABLE IF EXISTS AmenitiesIn;
DROP TABLE IF EXISTS Provides;
DROP TABLE IF EXISTS Interests;
DROP TABLE IF EXISTS Pets;
DROP TABLE IF EXISTS PetPolicy;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS ApartmentUnit;
DROP TABLE IF EXISTS ApartmentBuilding;
DROP TABLE IF EXISTS Amenities;


-- According to the ER diagram, phone and email are multi-valued attributes, so they should be represented by separate table(s); For simplicity, we are making them single-valued attributes here.
CREATE TABLE Users (
    username VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    DOB date NOT NULL,
    gender VARCHAR(20) NOT NULL,
    email VARCHAR(50),
    Phone VARCHAR(20),
    passwd VARCHAR(200) -- you may change this to larger size if not enough for hashed passwd
);

CREATE TABLE Pets (
   PetName VARCHAR(50) NOT NULL,
   PetType VARCHAR(50) NOT NULL,
   PetSize VARCHAR(20) NOT NULL,
   username VARCHAR(20) NOT NULL,
   FOREIGN KEY (username) REFERENCES Users (username),
   PRIMARY KEY (PetName,PetType,username)
);

CREATE TABLE ApartmentBuilding(
    CompanyName VARCHAR(20) NOT NULL,
    BuildingName VARCHAR(20) NOT NULL,
    AddrNum INT NOT NULL,
    AddrStreet VARCHAR(20) NOT NULL,
    AddrCity VARCHAR(20) NOT NULL,
    AddrState VARCHAR(5) NOT NULL,
    AddrZipCode VARCHAR(5) NOT NULL,
    YearBuilt YEAR NOT NULL,
    PRIMARY KEY (CompanyName, BuildingName)
);

CREATE TABLE ApartmentUnit (
   UnitRentID INT NOT NULL AUTO_INCREMENT,
   CompanyName VARCHAR(20) NOT NULL,
   BuildingName VARCHAR(20) NOT NULL,
   unitNumber VARCHAR(10) NOT NULL,
   MonthlyRent INT NOT NULL,
   squareFootage INT NOT NULL,
   AvailableDateForMoveIn date NOT NULL,
   FOREIGN KEY (CompanyName,BuildingName) REFERENCES ApartmentBuilding (CompanyName,BuildingName),
   PRIMARY KEY (UnitRentID)
);

CREATE TABLE Rooms(
    name VARCHAR(20) NOT NULL,
    squareFootage INT NOT NULL,
    description VARCHAR(50) NOT NULL,
    UnitRentID INT NOT NULL,
    FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit (UnitRentID),
    PRIMARY KEY (name,UnitRentID)
);

CREATE TABLE PetPolicy(
    CompanyName VARCHAR(20) NOT NULL,
    BuildingName VARCHAR(20) NOT NULL,
    PetType VARCHAR(50) NOT NULL,
    PetSize VARCHAR(20) NOT NULL,
    isAllowed BOOLEAN NOT NULL,
    RegistrationFee INT,
    MonthlyFee INT,
    FOREIGN KEY (CompanyName,BuildingName) REFERENCES ApartmentBuilding (CompanyName,BuildingName),
    PRIMARY KEY (CompanyName,BuildingName,PetType,PetSize)
);

CREATE TABLE Amenities(
    aType VARCHAR(20) NOT NULL,
    Description VARCHAR(100) NOT NULL,
    PRIMARY KEY (aType)
);

CREATE TABLE Interests(
    username VARCHAR(20) NOT NULL,
    UnitRentID INT NOT NULL,
    RoommateCnt TINYINT NOT NULL,
    MoveInDate date NOT NULL,
    FOREIGN KEY (username) REFERENCES Users (username),
    FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit (UnitRentID),
    PRIMARY KEY (username, UnitRentID)
);

CREATE TABLE AmenitiesIn(
    aType VARCHAR(20) NOT NULL,
    UnitRentID INT NOT NULL,
    FOREIGN KEY (aType) REFERENCES Amenities (aType),
    FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit (UnitRentID),
    PRIMARY KEY (aType, UnitRentID)
);


CREATE TABLE Provides(
    aType VARCHAR(20) NOT NULL,
    CompanyName VARCHAR(20) NOT NULL,
    BuildingName VARCHAR(20) NOT NULL,
    Fee INT NOT NULL,
    waitingList INT NOT NULL,
    FOREIGN KEY (aType) REFERENCES Amenities (aType),
    FOREIGN KEY (CompanyName,BuildingName) REFERENCES ApartmentBuilding (CompanyName,BuildingName),
    PRIMARY KEY (CompanyName,BuildingName,aType)
);