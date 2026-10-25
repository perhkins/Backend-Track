# Backend Track

This repository contains the exercises and projects for the backend track.

## Folder structure

```text
Backend Track/
├── Section1/
│   ├── two_sum_descending.py
│   └── two_sum_unsorted.py
└── Section2/
    └── booking-api/
        ├── app/
        ├── tests/
        ├── booking.db
        ├── requirements.txt
        └── README.md
```

## Section 1: Two-sum exercises

The Section 1 files are standalone Python scripts. Each script includes example
test cases that run when the file is executed.

From the repository root, change to the Section 1 directory:

```powershell
cd Section1
```

Run the version for a descending sorted list:

```powershell
python two_sum_descending.py
```

Run the version for an unsorted list:

```powershell
python two_sum_unsorted.py
```

To return to the repository root:

```powershell
cd ..
```

## Section 2: Booking API

Section 2 contains a FastAPI event RSVP service. For setup, API usage,
documentation links, example requests, and testing instructions, see the
[Section 2 booking API README](Section2/booking-api/README.md).

To work with the booking API from the repository root, change to its directory:

```powershell
cd Section2\booking-api
```

The detailed README includes the commands to create a virtual environment,
install dependencies, start the API, and run its tests.
