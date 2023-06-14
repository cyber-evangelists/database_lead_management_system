
from pymongo import MongoClient
from decouple import config
import re,json
from itertools import islice
from bson.objectid import ObjectId

from LeadManagementApp.global_variables import columns_to_check_existence,excluded_columns_from_filters,columns_that_have_list

def redirect_if_authenticated(user):
    return not user.is_authenticated

# connect to mongoDB database
def get_db_handle():
    client = MongoClient(host=config("DB_HOST"),
                        port=int(config("DB_PORT")),
                        username=config("DB_USER"),
                        password=config("DB_PASSWORD")
                        )
    db_handle = client[config("DB_NAME")]
    return db_handle, client

# get the columns list from the mongo db database
def get_leads_columns():
    try:
        db_handle,db_client = get_db_handle()
        columns = db_handle[config("COLUMNS_COLLECTION")].find({})[0]['columns']
        return columns
    except:
        return []

def get_leads_data(start,length,query):
    try:
        db_handle,db_client = get_db_handle()
        leads_collection = db_handle[config("LEADS_COLLECTION")]
        columns = get_leads_columns()
        leads_documents = leads_collection.find(query,{"_id": 0})
        leads_data = []
        for lead in leads_documents:
            leads_values = {key: None for key in columns}
            leads_values = {k: v if v else lead["data"].get(k) for k, v in leads_values.items()}
            leads_data.append(list(leads_values.values()))
        return leads_data
    except Exception as e:
        print(e)
        return []

def get_filters():
    filters = []
    try:
        db_handle,db_client = get_db_handle()
        filters_collection = db_handle[config("FILTERS_COLLECTION")]
        for filter_document in filters_collection.find({}):
            filters.append({
                "column": filter_document["column"],
                "values": filter_document["values"]
            })
    except Exception as e:
        print(e)
    return filters

def processCsvFile(reader):
    header = next(reader)
    if check_columns_validity(header):
        if add_new_columns(header):
            chunk_size = 1000  # chunk size
            while True:
                chunk = list(islice(reader, chunk_size))
                if not chunk:
                    break
                add_new_leads(header,chunk)
            return {'error':0,'message':'The process was done successfully!'}
        else:
            return {'error':1,'message':'Error when adding the new columns to the database, please try again later!'}
    else:
        return {'error':1,'message':'Please check The columns names, they are considered valid if it contains only alphanumeric characters and underscores '+header}

def check_columns_validity(header):
    # Check the validity of each column name
    for column in header:
        if column != "":
            # Remove leading and trailing whitespaces
            column = column.replace(" ", "_")
            # Check if the column name contains only alphanumeric characters and underscores
            if not re.match("^[a-zA-Z0-9_]+$", column):
                return False
    return True

def add_new_columns(header):
    try:
        old_columns = get_leads_columns()
        old_columns_lowercase = [x.lower() for x in old_columns]
        new_columns = []
        for item in header:
            if item.lower() not in old_columns_lowercase:
                new_columns.append(item)

        columns = old_columns+new_columns
        
        db_handle,db_client = get_db_handle()
        columns_collection = db_handle[config("COLUMNS_COLLECTION")]

        query = {"_id": ObjectId(config("COLUMNS_ID"))}
        newvalues = { "$set": {"columns":columns} }
        columns_collection.update_one(query, newvalues)
        return True
    except Exception as e:
        print(e)
        return False

def add_new_leads(header,chunk):
    try:
        db_handle,db_client = get_db_handle()
        leads_collection = db_handle[config("LEADS_COLLECTION")]
        filters_collection = db_handle[config("FILTERS_COLLECTION")]
        columns_existence_exist = check_columns_existence(header)
        for row in chunk:
            add_new_lead(leads_collection,filters_collection,header,row,columns_existence_exist)
    except Exception as e:
        print(e)
    return

def check_columns_existence(header):
    #we check at first if the columns used to check existence are there or not
    header_lowercase = [x.lower() for x in header]
    for column in columns_to_check_existence:
        if column.lower() not in header_lowercase:
            return False
    return True

def add_new_lead(leads_collection,filters_collection,header,row,columns_existence_exist):
    lead_values = {}
    for i, column in enumerate(header):
        value = row[i]
        if column not in columns_that_have_list:
            lead_values = {**lead_values,**{column:value}}
        else:
            values = value.split(',')
            lead_values = {**lead_values,**{column:values}}
        if column not in excluded_columns_from_filters:
            update_filters_collection(filters_collection,column,value)
    if columns_existence_exist:
        query = {"data."+columns_to_check_existence[0]: lead_values[columns_to_check_existence[0]], "data."+columns_to_check_existence[1]: lead_values[columns_to_check_existence[1]], "data."+columns_to_check_existence[2]: lead_values[columns_to_check_existence[2]]}
        lead = leads_collection.find_one(query)
        if lead:
            lead_values = check_exists_columns_values(lead,lead_values)
            leads_collection.update_one(query, {"$set": {"data": lead_values}}, upsert=False)
        else:
            leads_collection.insert_one({"data": lead_values})
    else:
        leads_collection.insert_one({"data": lead_values})

def get_filters_from_request(request):
    try:
        data = request.POST
        query = {}
        for field, value in data.items():
            if field != "csrfmiddlewaretoken" and value:
                values = [x for x in data.getlist(field) if x != '']
                query['data.'+field] = {"$in": values} 
        return query
    except Exception as e:
        print(e)
        return {}

def check_exists_columns_values(lead,lead_values):
    try:
        oiginal_lead_values = lead["data"]
        database_columns = get_leads_columns()
        for column in database_columns:
            if column in lead_values and oiginal_lead_values[column] != lead_values[column]:
                if column not in columns_that_have_list:
                    if lead_values[column] != "":
                        current_version = 1
                        while True:
                            versioned_attribute = f"{column}{current_version}"
                            if versioned_attribute not in oiginal_lead_values:
                                break
                            if lead_values[column] == oiginal_lead_values[versioned_attribute]:
                                current_version = -1
                                break
                            current_version += 1
                        if current_version != -1 :
                            add_new_columns([versioned_attribute])
                            oiginal_lead_values[versioned_attribute] = lead_values[column]
                else:
                    oiginal_lead_values[column] = list(set(oiginal_lead_values[column] + lead_values[column]))

    except Exception as e:
        print("here",e)
        return oiginal_lead_values
    else:
        return oiginal_lead_values

def update_filters_collection(filters_collection,column_name,value):
    try:
        values_list = []
        filter_document = filters_collection.find_one({"column": column_name})
        if filter_document:
            if column_name not in columns_that_have_list:
                if value not in filter_document["values"] and value != "":
                    values_list = filter_document["values"]
                    values_list.append(value)
            else:
                values_list = filter_document["values"]
                new_values_list = value.split(",")
                for element_value in new_values_list:
                    if element_value not in values_list and element_value != "":
                        values_list.append(element_value)
            filters_collection.update_one(
                {"column": column_name},
                {"$set": {"values": values_list}}
            )
        else:
            if column_name not in columns_that_have_list:
                if value != "":
                    values_list = [value]
            else:
                values_list = value.split(",")
            filters_collection.insert_one({"column": column_name, "values": values_list})
    except Exception as e:
        print(e)
        pass

