INSERT INTO library (libName, libraryDept, numFloors, libAddress, reservationLink)
VALUES ('Grainger', 'Engineering', 4, '1301 W Springfield Ave, Urbana, IL 61801', 'https://uiuc.libcal.com/spaces?lid=3606'),
	('Chemistry Library', 'Chemistry', 1, '505 S Mathews Ave, Urbana, IL 61801', 'https://uiuc.libcal.com/spaces?lid=5903'),
	('Main Library', 'LAS', 2, '1408 W Gregory Dr, Urbana, IL 61801', 'https://uiuc.libcal.com/spaces?lid=3608'),
	('UGL', 'LAS', 2, '1402 W Gregory Dr, Urbana, IL 61801', 'https://uiuc.libcal.com/spaces?lid=3152'),
	('ACES Library', 'ACES', 3, '1101 S Goodwin Ave, Urbana, IL 61801', NULL);

INSERT INTO floorSection (libName, floorNum, section, numSeats, studyEnv)
VALUES ('Grainger', 4, 'West', 107, 'collaborative'),
	('Grainger', 4, 'Central', 102, 'collaborative'),
	('Grainger', 4, 'EWS', 100, 'EWS'),
	('Grainger', 4, 'East', 32, 'collaborative'),
	('Grainger', 3, 'All', 85, 'quiet'),
	('Grainger', 2, 'All', 557, 'quiet'),
	('Grainger', 1, 'West', 0, 'collaborative'),
	('Grainger', 1, 'EWS', 0, 'collaborative'),
	('Chemistry Library', 1, 'Noyes', 77, 'quiet'),
	('Main Library', 1, 'All', 264, 'quiet'),
	('Main Library', 2, 'All', 434, 'quiet'),
	('UGL', 1, 'All', 384, 'collaborative'),
	('UGL', 2, 'All', 720, 'quiet');
