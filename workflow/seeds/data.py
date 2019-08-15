# Extension Service

projectextensions = [
    {"workflowlevel2_uuid": "8132d789-9580-45ad-b22a-9384bce0eed6", "id": "not needed"},
    {"workflowlevel2_uuid": "6f015067-db3e-40be-8f87-8b20fa347752", "id": "not needed"},
    {"workflowlevel2_uuid": "9e3bda19-49e5-428a-a2cc-ef03153f14bb", "id": "not needed"},
    {"workflowlevel2_uuid": "7b504be7-36e3-4196-8c60-227b78f8ae96", "id": "not needed"},
    {"workflowlevel2_uuid": "999d0b08-759f-49d6-b121-e312c3ea17c5", "id": "not needed"},
]


# Location Service

profiletypes = [
    {"id": 79, "name": "billing", "is_global": True},
    {"id": 80, "name": "object", "is_global": True},
    {"id": 81, "name": "object_with_billing", "is_global": True},
]

siteprofiles = [
    {
        "uuid": "900498a7-8630-4c7c-9762-2447cc2178ce",
        "id": "900498a7-8630-4c7c-9762-2447cc2178ce",
        "country": "DE",
        "name": "Friedrichstraße 233, 10969 Berlin",
        "address_line1": "Friedrichstraße 233",
        "address_line2": "",
        "address_line3": "",
        "address_line4": "",
        "postcode": "10969",
        "city": "Berlin",
        "administrative_level1": "",
        "administrative_level2": "",
        "administrative_level3": "",
        "administrative_level4": "",
        "latitude": "0.0000000000000000",
        "longitude": "0.0000000000000000",
        "notes": "",
        "workflowlevel2_uuid": [
            "8132d789-9580-45ad-b22a-9384bce0eed6"
        ],
        "profiletype": 81
    },
    {
        "uuid": "485234bd-1bd6-49b9-81b9-7d84161b6b39",
        "id": "485234bd-1bd6-49b9-81b9-7d84161b6b39",
        "country": "DE",
        "name": "Lehmbruckstraße 12, 10245 Berlin",
        "address_line1": "Lehmbruckstraße 12",
        "address_line2": "",
        "address_line3": "",
        "address_line4": "",
        "postcode": "10245",
        "city": "Berlin",
        "administrative_level1": "",
        "administrative_level2": "",
        "administrative_level3": "",
        "administrative_level4": "",
        "latitude": "0.0000000000000000",
        "longitude": "0.0000000000000000",
        "notes": "",
        "workflowlevel2_uuid": [
            "999d0b08-759f-49d6-b121-e312c3ea17c5"
        ],
        "profiletype": 80
    },
    {
        "uuid": "5b04b3aa-f18e-416b-bf5b-bc9c86786159",
        "id": "5b04b3aa-f18e-416b-bf5b-bc9c86786159",
        "country": "DE",
        "name": "Ossastraße 44, 12045 Berlin",
        "address_line1": "Ossastraße 44",
        "address_line2": "",
        "address_line3": "",
        "address_line4": "",
        "postcode": "12045",
        "city": "Berlin",
        "administrative_level1": "",
        "administrative_level2": "",
        "administrative_level3": "",
        "administrative_level4": "",
        "latitude": "0.0000000000000000",
        "longitude": "0.0000000000000000",
        "notes": "",
        "workflowlevel2_uuid": [
            "6f015067-db3e-40be-8f87-8b20fa347752"
        ],
        "profiletype": 80
    },
    {
        "uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "id": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "country": "DE",
        "name": "Tempelhofer Ufer 13, 10963 Berlin",
        "address_line1": "Tempelhofer Ufer 13",
        "address_line2": "",
        "address_line3": "",
        "address_line4": "",
        "postcode": "10963",
        "city": "Berlin",
        "administrative_level1": "",
        "administrative_level2": "",
        "administrative_level3": "",
        "administrative_level4": "",
        "latitude": "0.0000000000000000",
        "longitude": "0.0000000000000000",
        "notes": "",
        "workflowlevel2_uuid": [
            "9e3bda19-49e5-428a-a2cc-ef03153f14bb"
        ],
        "profiletype": 81
    },
    {
        "uuid": "5fa79e8b-599c-4a70-97ef-989f0c823e5d",
        "id": "5fa79e8b-599c-4a70-97ef-989f0c823e5d",
        "country": "DE",
        "name": "Urbanstraße 76, 10967 Berlin",
        "address_line1": "Urbanstraße 76",
        "address_line2": "",
        "address_line3": "",
        "address_line4": "",
        "postcode": "10967",
        "city": "Berlin",
        "administrative_level1": "",
        "administrative_level2": "",
        "administrative_level3": "",
        "administrative_level4": "",
        "latitude": "0.0000000000000000",
        "longitude": "0.0000000000000000",
        "notes": "",
        "workflowlevel2_uuid": [
            "7b504be7-36e3-4196-8c60-227b78f8ae96"
        ],
        "profiletype": 80
    }
]


# CRM Service

contacts = [
    {
        "uuid": "61a012e5-d70b-4801-acb3-507b913fcd54",
        "id": "61a012e5-d70b-4801-acb3-507b913fcd54",
        "first_name": "Max",
        "last_name": "Mustermann",
        "customer_type": "customer",
        "company": "Mustermann GmbH",
        "siteprofile_uuids": ["900498a7-8630-4c7c-9762-2447cc2178ce"],
        "emails": [{"type": "office", "email": "mustermann@mustermann.de"}],
        "phones": [{"type": "home", "number": "030376262666"}],
        "notes": None,
        "workflowlevel1_uuids": ["49a4c9d7-8b72-434b-8a48-24540f65a2f3"],
        "workflowlevel2_uuids": [
            "8132d789-9580-45ad-b22a-9384bce0eed6",
            "6f015067-db3e-40be-8f87-8b20fa347752",
        ],
        "contact_type": None,
    },
    {
        "uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "id": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "first_name": "Mia",
        "last_name": "Musterfrau",
        "customer_type": "customer",
        "company": None,
        "siteprofile_uuids": ["551629e8-bb28-4734-a3e4-7edb239854b2"],
        "emails": [{"type": "office", "email": "mia.musterfrau@gmail.com"}],
        "phones": [{"type": "home", "number": "01721648387"}],
        "notes": None,
        "workflowlevel1_uuids": ["49a4c9d7-8b72-434b-8a48-24540f65a2f3"],
        "workflowlevel2_uuids": [
            "9e3bda19-49e5-428a-a2cc-ef03153f14bb",
            "7b504be7-36e3-4196-8c60-227b78f8ae96",
            "999d0b08-759f-49d6-b121-e312c3ea17c5",
        ],
        "contact_type": None,
    },
]

appointments = [
    {
        "uuid": "432aa435-f9ec-4984-87d3-31f1b2a9388e",
        "id": "432aa435-f9ec-4984-87d3-31f1b2a9388e",
        "notes": [
            {"id": 1971, "note": "", "type": 1},
            {"id": 1972, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-07-30T07:00:00+02:00",
        "end_date": "2019-07-30T09:00:00+02:00",
        "type": ["beratung"],
        "address": "Friedrichstraße 233, 10969 Berlin",
        "siteprofile_uuid": "900498a7-8630-4c7c-9762-2447cc2178ce",
        "invitee_uuids": ["3418abb1-faff-4f38-86d9-606f3f542ef5"],
        "workflowlevel2_uuids": ["8132d789-9580-45ad-b22a-9384bce0eed6"],
        "contact_uuid": "61a012e5-d70b-4801-acb3-507b913fcd54",
        "summary": "",
    },
    {
        "uuid": "878db099-b8c1-4482-b4a8-11e26168c933",
        "id": "878db099-b8c1-4482-b4a8-11e26168c933",
        "notes": [
            {"id": 1973, "note": "Neuinstallation Vitodens 200", "type": 1},
            {"id": 1974, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-07-31T07:00:00+02:00",
        "end_date": "2019-07-31T16:00:00+02:00",
        "type": ["installation"],
        "address": "Ossastraße 44, 12045 Berlin",
        "siteprofile_uuid": "5b04b3aa-f18e-416b-bf5b-bc9c86786159",
        "invitee_uuids": [
            "44852b4a-4e80-448e-8936-71c4c294a1b7",
            "3418abb1-faff-4f38-86d9-606f3f542ef5",
            "40517e88-26cb-4b34-853f-ed383c1af0d6",
        ],
        "workflowlevel2_uuids": ["6f015067-db3e-40be-8f87-8b20fa347752"],
        "contact_uuid": "61a012e5-d70b-4801-acb3-507b913fcd54",
        "summary": "",
    },
    {
        "uuid": "edeb1722-5b43-4eb0-ae52-b5598e40e704",
        "id": "edeb1722-5b43-4eb0-ae52-b5598e40e704",
        "notes": [
            {"id": 1976, "note": "", "type": 3},
            {"id": 1975, "note": "Bitte Standardwartung durchführen", "type": 1},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-01T07:00:00+02:00",
        "end_date": "2019-08-01T09:00:00+02:00",
        "type": ["wartung"],
        "address": "Tempelhofer Ufer 13, 10963 Berlin",
        "siteprofile_uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "invitee_uuids": ["44852b4a-4e80-448e-8936-71c4c294a1b7"],
        "workflowlevel2_uuids": ["9e3bda19-49e5-428a-a2cc-ef03153f14bb"],
        "contact_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "summary": "",
    },
    {
        "uuid": "ed4c7e5a-5211-486e-a0ca-fcde746a8e2e",
        "id": "ed4c7e5a-5211-486e-a0ca-fcde746a8e2e",
        "notes": [
            {"id": 1977, "note": "Bitte Standardwartung durchführen", "type": 1},
            {"id": 1978, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-01T10:00:00+02:00",
        "end_date": "2019-08-01T12:00:00+02:00",
        "type": ["wartung"],
        "address": "Urbanstraße 76, 10967 Berlin",
        "siteprofile_uuid": "5fa79e8b-599c-4a70-97ef-989f0c823e5d",
        "invitee_uuids": ["44852b4a-4e80-448e-8936-71c4c294a1b7"],
        "workflowlevel2_uuids": ["7b504be7-36e3-4196-8c60-227b78f8ae96"],
        "contact_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "summary": "",
    },
    {
        "uuid": "9ba34824-a224-4da9-8ace-e24a1006c231",
        "id": "9ba34824-a224-4da9-8ace-e24a1006c231",
        "notes": [
            {"id": 1979, "note": "Bitte Standardwartung durchführen", "type": 1},
            {"id": 1980, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-01T13:00:00+02:00",
        "end_date": "2019-08-01T15:00:00+02:00",
        "type": ["wartung"],
        "address": "Lehmbruckstraße 12, 10245 Berlin",
        "siteprofile_uuid": "485234bd-1bd6-49b9-81b9-7d84161b6b39",
        "invitee_uuids": ["44852b4a-4e80-448e-8936-71c4c294a1b7"],
        "workflowlevel2_uuids": ["999d0b08-759f-49d6-b121-e312c3ea17c5"],
        "contact_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "summary": "",
    },
    {
        "uuid": "951609b6-32e9-43e6-8f24-692462a81496",
        "id": "951609b6-32e9-43e6-8f24-692462a81496",
        "notes": [
            {"id": 1981, "note": "", "type": 1},
            {"id": 1982, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-02T07:00:00+02:00",
        "end_date": "2019-08-02T16:00:00+02:00",
        "type": ["installation"],
        "address": "Friedrichstraße 233, 10969 Berlin",
        "siteprofile_uuid": "900498a7-8630-4c7c-9762-2447cc2178ce",
        "invitee_uuids": [
            "44852b4a-4e80-448e-8936-71c4c294a1b7",
            "3418abb1-faff-4f38-86d9-606f3f542ef5",
            "40517e88-26cb-4b34-853f-ed383c1af0d6",
        ],
        "workflowlevel2_uuids": ["8132d789-9580-45ad-b22a-9384bce0eed6"],
        "contact_uuid": "61a012e5-d70b-4801-acb3-507b913fcd54",
        "summary": "",
    },
    {
        "uuid": "ae4bde84-7f02-436f-b666-70d032ee8d61",
        "id": "ae4bde84-7f02-436f-b666-70d032ee8d61",
        "notes": [
            {"id": 1984, "note": "", "type": 3},
            {"id": 1983, "note": "Bitte Ventile prüfen und austauschen.", "type": 1},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-09T07:00:00+02:00",
        "end_date": "2019-08-09T09:00:00+02:00",
        "type": ["reparatur"],
        "address": "Tempelhofer Ufer 13, 10963 Berlin",
        "siteprofile_uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "invitee_uuids": [
            "44852b4a-4e80-448e-8936-71c4c294a1b7",
            "3418abb1-faff-4f38-86d9-606f3f542ef5",
            "40517e88-26cb-4b34-853f-ed383c1af0d6",
        ],
        "workflowlevel2_uuids": ["9e3bda19-49e5-428a-a2cc-ef03153f14bb"],
        "contact_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "summary": "",
    },
    {
        "uuid": "138b1db2-322d-4f4f-bd04-a81737adc15e",
        "id": "138b1db2-322d-4f4f-bd04-a81737adc15e",
        "notes": [
            {"id": 1985, "note": "Bitte Ventile prüfen und austauschen.", "type": 1},
            {"id": 1986, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-16T07:00:00+02:00",
        "end_date": "2019-08-16T09:00:00+02:00",
        "type": ["reparatur"],
        "address": "Tempelhofer Ufer 13, 10963 Berlin",
        "siteprofile_uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "invitee_uuids": [
            "44852b4a-4e80-448e-8936-71c4c294a1b7",
            "3418abb1-faff-4f38-86d9-606f3f542ef5",
            "40517e88-26cb-4b34-853f-ed383c1af0d6",
        ],
        "workflowlevel2_uuids": ["9e3bda19-49e5-428a-a2cc-ef03153f14bb"],
        "contact_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "summary": "",
    },
    {
        "uuid": "bcc6c746-faab-489d-9d37-eb7d431e4e9d",
        "id": "bcc6c746-faab-489d-9d37-eb7d431e4e9d",
        "notes": [
            {"id": 1987, "note": "Bitte Ventile prüfen und austauschen.", "type": 1},
            {"id": 1988, "note": "", "type": 3},
        ],
        "name": "Kupfer Appointment",
        "start_date": "2019-08-23T07:00:00+02:00",
        "end_date": "2019-08-23T09:00:00+02:00",
        "type": ["installation"],
        "address": "Tempelhofer Ufer 13, 10963 Berlin",
        "siteprofile_uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "invitee_uuids": [
            "44852b4a-4e80-448e-8936-71c4c294a1b7",
            "3418abb1-faff-4f38-86d9-606f3f542ef5",
            "40517e88-26cb-4b34-853f-ed383c1af0d6",
        ],
        "workflowlevel2_uuids": ["9e3bda19-49e5-428a-a2cc-ef03153f14bb"],
        "contact_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "summary": "",
    },
]


# Product Service

product_categories = [
    {
        "uuid": "75207588-9956-4331-af63-4b0307ac09aa",
        "id": "75207588-9956-4331-af63-4b0307ac09aa",
        "name": "HEATING_SYSTEM",
        "is_global": True,
        "parent": None,
    },
    {
        "uuid": "6989cbe9-307f-49f2-b841-f40c74acf840",
        "id": "6989cbe9-307f-49f2-b841-f40c74acf840",
        "name": "GAS_CONDENSING",
        "is_global": True,
        "level": 1,
        "parent": "75207588-9956-4331-af63-4b0307ac09aa",
    },
]

products = [
    {
        "id": "58e599ca-e6e7-48bd-9ca1-29e988ce7a74",
        "category_display": "HEATING_SYSTEM",
        "subcategory_display": "GAS_CONDENSING",
        "part_number": "",
        "installation_date": "2019-07-02",
        "recurring_check_interval": "12",
        "notes": "",
        "workflowlevel2_uuid": "999d0b08-759f-49d6-b121-e312c3ea17c5",
        "name": "Vitodens 200",
        "make": "Viessmann",
        "type": "",
        "reference_id": "9049384729385732",
        "organization_uuid": "a7d7f137-94e4-4fa9-8ac1-3456a1611a71",
        "category": "6989cbe9-307f-49f2-b841-f40c74acf840",
    },
    {
        "id": "9f20afc3-bd55-4d28-b163-a6b810963a4e",
        "category_display": "HEATING_SYSTEM",
        "subcategory_display": "GAS_CONDENSING",
        "part_number": "",
        "installation_date": "2019-07-30",
        "recurring_check_interval": "12",
        "notes": "",
        "workflowlevel2_uuid": "8132d789-9580-45ad-b22a-9384bce0eed6",
        "name": "Vitodens 200",
        "make": "Viessmann",
        "type": "",
        "reference_id": "9049384729385732",
        "organization_uuid": "a7d7f137-94e4-4fa9-8ac1-3456a1611a71",
        "category": "6989cbe9-307f-49f2-b841-f40c74acf840",
    },
]


# TimeTracking Service

time_events = []

time_log_entries = []


# Documents Service

documents = [
    {
        "id": 22849,
        "file_description": "undefined",
        "file_name": "Pic_1.jpg",
        "file_type": "jpg",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["8132d789-9580-45ad-b22a-9384bce0eed6"],
    },
    {
        "id": 22850,
        "file_description": "undefined",
        "file_name": "Pic_2.png",
        "file_type": "png",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["8132d789-9580-45ad-b22a-9384bce0eed6"],
    },
    {
        "id": 22851,
        "file_description": "undefined",
        "file_name": "Pic_3.jpg",
        "file_type": "jpg",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["8132d789-9580-45ad-b22a-9384bce0eed6"],
    },
    {
        "id": 22852,
        "file_description": "undefined",
        "file_name": "Datenblatt_Vitodens.pdf",
        "file_type": "pdf",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["8132d789-9580-45ad-b22a-9384bce0eed6"],
    },
    {
        "id": 22853,
        "file_description": "undefined",
        "file_name": "Pic_1.jpg",
        "file_type": "jpg",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["999d0b08-759f-49d6-b121-e312c3ea17c5"],
    },
    {
        "id": 22854,
        "file_description": "undefined",
        "file_name": "Pic_3.jpg",
        "file_type": "jpg",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["999d0b08-759f-49d6-b121-e312c3ea17c5"],
    },
    {
        "id": 22855,
        "file_description": "undefined",
        "file_name": "Pic_2.png",
        "file_type": "png",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["999d0b08-759f-49d6-b121-e312c3ea17c5"],
    },
    {
        "id": 22856,
        "file_description": "undefined",
        "file_name": "Datenblatt_Vitodens.pdf",
        "file_type": "pdf",
        "organization_uuid": None,
        "workflowlevel2_uuids": ["999d0b08-759f-49d6-b121-e312c3ea17c5"],
    },
]

SEED_DATA = {
    "extensions": {
        "projectextensions": {
            "data": projectextensions,
            "update_fields": {"workflowlevel2_uuid": "workflowlevel2"},
        }
    },
    "location": {
        # 'profiletypes': {
        #     'data': profiletypes,
        # },
        "siteprofiles": {
            "data": siteprofiles,
            "update_fields": {
                "workflowlevel2_uuid": "workflowlevel2",
                "profiletype": "profiletypes",
            },
        }
    },
    "crm": {
        "contact": {
            "data": contacts,
            "update_fields": {
                "siteprofile_uuids": "siteprofiles",
                "workflowlevel1_uuids": "workflowlevel1",
                "workflowlevel2_uuids": "workflowlevel2",
            },
        },
        "appointment": {
            "data": appointments,
            "update_fields": {
                "contact_uuid": "contact",
                "siteprofile_uuid": "siteprofiles",
                "workflowlevel2_uuids": "workflowlevel2",
            },
            "update_dates": {
                "start_date": "week_of_the_org_created_week",
                "end_date": "week_of_the_org_created_week",
            },
            "set_fields": {
                "invitee_uuids": "org_core_user_uuids",
            },
        }
    },
    "products": {
        # 'categories?is_global=true': {
        #     'data': product_categories,
        # },
        "products": {
            "data": products,
            "update_fields": {
                "category": "categories",
                "workflowlevel2_uuid": "workflowlevel2",
            },
        },
    },
    "timetracking": {
        "time-event": {
            "validate": False,
            "data": time_events,
            "update_fields": {
                "workflowlevel2_uuid": "workflowlevel2",
                "appointment_uuid": "appointment",
            },
            # "set_fields": {
            #     "core_user_uuid": "org_core_user_uuids[0]",
            # },
        },
        "time-log-entry": {
            "validate": False,
            "data": time_log_entries,
            "update_fields": {
                "time_event": "time-event",
            },
            "update_dates": {
                "start_time": 0,
                "end_time": {
                    "hours": 1,
                    "minutes": 25,
                },
            },
        },
    },
    "documents": {
        "documents": {
            "validate": False,
            "data": documents,
            "upload_files": {
                "file_name_field": "documents_file",
            },
            "set_fields": {
                "organization_uuid": "organization_uuid",
            },
        },
    },
}


# Bifrost Data

workflowleveltypes = [
    {"uuid": "e2bafb25-c6ee-45c1-93bf-82e3206f8f29", "name": "INSTALLATION"},
    {"uuid": "c17709b0-3acf-4a93-9d14-a5a5f59fcb77", "name": "MAINTENANCE"},
    {"uuid": "ad4937f3-0282-4d66-ac8c-4d9b903ee1cd", "name": "REPAIR"},
    {"uuid": "eb6fd665-af47-429d-aad4-8cf6622f656b", "name": "REPLACEMENT"},
    {"uuid": "9af16012-9f8a-40ce-827e-4ed6be711677", "name": "EMERGENCY"},
    {"uuid": "b0b81450-db28-4d1b-b036-9cf5c36db4be", "name": "OTHERS"},
]

workflowlevel2s = [
    {
        "level2_uuid": "8132d789-9580-45ad-b22a-9384bce0eed6",
        "description": "Bitte neuen Kessel einbauen.",
        "name": "New Kupfer Project",
        "parent_workflowlevel2": 0,
        "end_date": "2019-08-22T00:00:00+02:00",
        "workflowlevel1": 18,
        "type": "e2bafb25-c6ee-45c1-93bf-82e3206f8f29",
    },
    {
        "level2_uuid": "6f015067-db3e-40be-8f87-8b20fa347752",
        "description": "Neuinstallation Vitodens 200",
        "name": "New Kupfer Project",
        "parent_workflowlevel2": 0,
        "workflowlevel1": 18,
        "type": "e2bafb25-c6ee-45c1-93bf-82e3206f8f29",
    },
    {
        "level2_uuid": "9e3bda19-49e5-428a-a2cc-ef03153f14bb",
        "description": "Bitte Standardwartung durchführen",
        "name": "New Kupfer Project",
        "parent_workflowlevel2": 0,
        "workflowlevel1": 18,
        "type": "c17709b0-3acf-4a93-9d14-a5a5f59fcb77",
    },
    {
        "level2_uuid": "7b504be7-36e3-4196-8c60-227b78f8ae96",
        "description": "Bitte Standardwartung durchführen",
        "name": "New Kupfer Project",
        "parent_workflowlevel2": 0,
        "workflowlevel1": 18,
        "type": "c17709b0-3acf-4a93-9d14-a5a5f59fcb77",
    },
    {
        "level2_uuid": "999d0b08-759f-49d6-b121-e312c3ea17c5",
        "description": "Bitte Standardwartung durchführen",
        "name": "New Kupfer Project",
        "parent_workflowlevel2": 0,
        "workflowlevel1": 18,
        "type": "c17709b0-3acf-4a93-9d14-a5a5f59fcb77",
    },
]


# Datamesh Data

join_records = [
    {
        "record_uuid": "61a012e5-d70b-4801-acb3-507b913fcd54",
        "related_record_uuid": "900498a7-8630-4c7c-9762-2447cc2178ce",
        "origin_model_name": "crmContact",
        "related_model_name": "locationSiteProfile",
    },
    {
        "record_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
        "related_record_uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
        "origin_model_name": "crmContact",
        "related_model_name": "locationSiteProfile",
    },
]
