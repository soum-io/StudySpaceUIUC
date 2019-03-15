CREATE TABLE student (
	username varchar(255) PRIMARY KEY,
	prefStudyEnv varchar(255),
	mainAddress varchar(255),
	favLibrary varchar(255),
	major varchar(255)
);

CREATE TABLE request (
	requestID int PRIMARY KEY,
	confidence int,
	initAddress varchar(255),
	prefEnv varchar(255),
	partySize int
);

CREATE TABLE library (
	libName varchar(255) PRIMARY KEY,
	libraryDept varchar(255),
	numFloors int,
	libAddress varchar(255),
	reservationLink varchar(255)
);


CREATE TABLE FloorSection (
	libName varchar(255),
	floorNum int NOT NULL,
	section varchar(255),
	numSeats int,
	studyEnv varchar(255),
	PRIMARY KEY(libName, floorNum, section),
	CONSTRAINT validStudyEnv CHECK (studyEnv in ('quiet', 'collaborative', 'private', 'EWS'))
);

CREATE TABLE hoursOfOP (
	libName varchar(255),
	dayOfWeek int,
	openTime int, 
	closeTime int,
	PRIMARY KEY(libName, dayOfWeek);
	CONSTRAINT validWeek CHECK(dayOfWeek <= 7)
);


CREATE TABLE recordData (
	dateTime date PRIMARY KEY,
	count int
);

CREATE TABLE specialDateRanges (
	eventName varchar(255) PRIMARY KEY,
	dateTimeStart date,
	dateTimeEnd date
);
