use roomio;
INSERT INTO ApartmentBuilding (CompanyName, BuildingName, AddrNum, AddrStreet, AddrCity, AddrState, AddrZipCode, YearBuilt) VALUES
('Cosmopolitan Housing', 'Cosmo 5', 123, 'Main St', 'Queens', 'NY', '11377', 2000),
('Linvilla', 'Red Apple', 456, 'Oak Ave', 'Los Angeles', 'CA', '98139', 2010),
('Nebraska Housing', 'Aksarben', 789, 'Pine Rd', 'Omaha', 'NE', '68132', 2015),
('Bostonians Unite', 'Bostons Dream', 321, 'Leaf Ln', 'Boston', 'MA', '01960', 2020);

INSERT INTO ApartmentUnit (CompanyName, BuildingName, unitNumber, MonthlyRent, squareFootage, AvailableDateForMoveIn) VALUES
('Cosmopolitan Housing', 'Cosmo 5', '101', 1200, 800, '2024-05-01'),
('Linvilla', 'Red Apple', '202', 1500, 950, '2024-06-01'),
('Nebraska Housing', 'Aksarben', '303', 1300, 850, '2024-07-01'),
('Bostonians Unite', 'Bostons Dream', '404', 1000, 700, '2024-08-01');

INSERT INTO Rooms (name, squareFootage, description, UnitRentID) VALUES
('Living Room', 200, 'Spacious with natural light', 1),
('Bedroom', 150, 'Cozy with a large closet', 1),
('Kitchen', 100, 'Modern appliances included', 1),
('Bathroom', 50, 'Fully tiled with modern fixtures', 1);

INSERT INTO PetPolicy (CompanyName, BuildingName, PetType, PetSize, isAllowed, RegistrationFee, MonthlyFee) VALUES
('Cosmopolitan Housing', 'Cosmo 5', 'Dog', 'Medium', TRUE, 200, 30),
('Linvilla', 'Red Apple', 'Cat', 'Small', TRUE, 100, 20),
('Linvilla', 'Red Apple', 'Dog', 'Large', FALSE, 0, 0),
('Bostonians Unite', 'Bostons Dream', 'Dog', 'Small', TRUE, 150, 25);

INSERT INTO Amenities (aType, Description) VALUES
('Pool', 'Outdoor swimming pool with lounge area'),
('Gym', 'Fully equipped 24/7 fitness center'),
('Parking', 'Covered parking space for residents'),
('Sauna', 'Steam and dry sauna available 24/7'),
('Lounge', 'Lounge area'),
('BBQ Area', 'BBQ'),
('Washer/Dryer', 'In Unit Washer Dryer'),
('Garbage Disposal', 'In unit garbage disposal'),
('Dishwasher', 'In unit dishwasher');

INSERT INTO Provides (aType, CompanyName, BuildingName, Fee, waitingList) VALUES
('Pool', 'Bostonians Unite', 'Bostons Dream', 0, 0),
('Gym', 'Bostonians Unite', 'Bostons Dream', 30, 5),
('Parking', 'Linvilla', 'Red Apple', 50, 10),
('Sauna', 'Cosmopolitan Housing', 'Cosmo 5', 20, 2),
('Lounge', 'Cosmopolitan Housing', 'Cosmo 5', 0, 0),
('BBQ Area', 'Nebraska Housing', 'Aksarben', 0, 3);

INSERT INTO AmenitiesIn (aType, UnitRentID) VALUES
('Washer/Dryer', 1),
('Garbage Disposal', 1),
('Washer/Dryer', 2),
('Sauna', 2),
('Garbage Disposal', 3),
('Dishwasher', 3);