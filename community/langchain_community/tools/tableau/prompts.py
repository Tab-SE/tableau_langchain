vds_instructions = """
Task:
Your job is to write requests to Tableau’s VizQL Data Service (VDS) API
to answer user questions that relate to data and analytics. The VDS API
accepts HTTP requests with a JSON payload describing how it must aggregate,
sort and filter the data as well as being able to write calculations on demand.

The VDS query is a JSON object that contains 2 fundamental components (See `Query` for more details).
    1. fields [required] - an array of fields that define the desired output of the query
        - See `FieldBase` for more information on supported properties
        - Aggregate fields according to the specifications found in `Function`
        - Refer to `SortDirection` for instructions on sorting
        - Find the necessary `fieldCaptions` to write the query by checking the `data_model` key
        containing additional metadata describing the data source
    2. filters [optional] - an array of filters to apply to the query. They can include fields
    that are not in the fields array. Supported filter types include:
        - [ Filter, MatchFilter, QuantitativeFilterBase, QuantitativeNumericalFilter, QuantitativeDateFilter, SetFilter, RelativeDateFilter, TopNFilter ]

Guidelines:
- Your task is to write the payload to retrieve data relevant to the user's question.
- Query all of the fields that seem useful or interesting including those that may only be
contextually related to the topics mentioned by the user even if additional transformations
or other actions are needed.
- Always aggregate data to avoid returning too granular of a result.
- Return query results verbatim

Output:
Your output must contain two sections
    1. "Query Plan": where you describe your reasoning: why you queried these fields,
    why you aggregated the data and why filters were applied to it. How does this satisfy the user query?
    2. "JSON_payload": the VDS payload you wrote to satisfy the user query according to the query plan and
    the instructions provided in the prompt

This is the template you must use:

Query Plan:
{insert query plan here}

JSON_payload:
{insert VDS payload here}
"""

vds_restrictions = """
Restrictions:
DO NOT HALLUCINATE FIELD NAMES.
Only use fields based on what is listed in the data_model
"""

vds_schema = {
    "FieldBase": {
        "type": "object",
        "description": "Common properties of a Field. A Field represents a column of data in a published datasource",
        "required": [ "fieldCaption" ],
        "properties": {
            "fieldCaption": {
                "type": "string",
                "description": "Either the name of a specific Field in the data source, or, in the case of a calculation, a user-supplied name for the calculation."
            },
            "fieldAlias": {
                "type": "string",
                "description": "An alternative name to give the field. Will only be used in Object format output."
            },
            "maxDecimalPlaces": {
                "type": "integer",
                "description": "The maximum number of decimal places. Any trailing 0s will be dropped. The maxDecimalPlaces value must be greater or equal to 0."
            },
            "sortDirection": {
                "$ref": "#/components/schemas/SortDirection"
            },
            "sortPriority": {
                "type": "integer",
                "description": "To enable sorting on a specific Field provide a sortPriority for that field, and that field will be sorted. The sortPriority provides a ranking of how to sort Fields when multiple Fields are being sorted. The highest priority (lowest number) Field is sorted first. If only 1 Field is being sorted, then any value may be used for sortPriority. SortPriority should be an integer greater than 0."
            }
        }
    },
    "Field": {
        "oneOf": [
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FieldBase"
                    }
                ],
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "fieldCaption": {},
                    "fieldAlias": {},
                    "maxDecimalPlaces": {},
                    "sortDirection": {},
                    "sortPriority": {}
                }
            },
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FieldBase"
                    }
                ],
                "type": "object",
                "required": [
                    "function"
                ],
                "additionalProperties": False,
                "properties": {
                    "function": {
                        "$ref": "#/components/schemas/Function"
                    },
                    "fieldCaption": {},
                    "fieldAlias": {},
                    "maxDecimalPlaces": {},
                    "sortDirection": {},
                    "sortPriority": {}
                }
            },
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FieldBase"
                    }
                ],
                "type": "object",
                "required": [
                    "calculation"
                ],
                "additionalProperties": False,
                "properties": {
                    "calculation": {
                        "type": "string",
                        "description": "A Tableau calculation which will be returned as a Field in the Query"
                    },
                    "fieldCaption": {},
                    "fieldAlias": {},
                    "maxDecimalPlaces": {},
                    "sortDirection": {},
                    "sortPriority": {}
                }
            }
        ]
    },
    "FieldMetadata": {
        "type": "object",
        "description": "Describes a field in the datasource that can be used to create queries.",
        "properties": {
            "fieldName": {
                "type": "string"
            },
            "fieldCaption": {
                "type": "string"
            },
            "dataType": {
                "type": "string",
                "enum": [
                    "INTEGER",
                    "REAL",
                    "STRING",
                    "DATETIME",
                    "BOOLEAN",
                    "DATE",
                    "SPATIAL",
                    "UNKNOWN"
                ]
            },
            "logicalTableId": {
                "type": "string"
            }
        }
    },
    "Filter": {
        "type": "object",
        "description": "A Filter to be used in the Query to filter on the datasource",
        "required": ["field", "filterType"],
        "properties": {
            "field": {
                "$ref": "#/components/schemas/FilterField"
            },
            "filterType": {
                "type": "string",
                "enum": [
                    "QUANTITATIVE_DATE",
                    "QUANTITATIVE_NUMERICAL",
                    "SET",
                    "MATCH",
                    "DATE",
                    "TOP"
                ]
            },
            "context": {
                "type": "boolean",
                "description": "Make the given filter a Context Filter, meaning that it's an independent filter. Any other filters that you set are defined as dependent filters because they process only the data that passes through the context filter",
                "default": False
            }
        },
        "discriminator": {
            "propertyName": "filterType",
            "mapping": {
                "QUANTITATIVE_DATE": "#/components/schemas/QuantitativeDateFilter",
                "QUANTITATIVE_NUMERICAL": "#/components/schemas/QuantitativeNumericalFilter",
                "SET": "#/components/schemas/SetFilter",
                "MATCH": "#/components/schemas/MatchFilter",
                "DATE": "#/components/schemas/RelativeDateFilter",
                "TOP": "#/components/schemas/TopNFilter"
            }
        }
    },
    "FilterField": {
        "oneOf": [
            {
                "required": ["fieldCaption"],
                "additionalProperties": False,
                "properties": {
                    "fieldCaption": {
                        "type": "string",
                        "description": "The caption of the field to filter on"
                    }
                }
            },
            {
                "required": ["fieldCaption", "function"],
                "additionalProperties": False,
                "properties": {
                    "fieldCaption": {
                        "type": "string",
                        "description": "The caption of the field to filter on"
                    },
                    "function": {
                        "$ref": "#/components/schemas/Function"
                    }
                }
            },
            {
                "required": ["calculation"],
                "additionalProperties": False,
                "properties": {
                    "calculation": {
                        "type": "string",
                        "description": "A Tableau calculation which will be used to Filter on"
                    }
                }
            }
        ]
    },
    "Function": {
        "type": "string",
        "description": "The standard set of Tableau aggregations which can be applied to a Field",
        "enum": [
            "SUM",
            "AVG",
            "MEDIAN",
            "COUNT",
            "COUNTD",
            "MIN",
            "MAX",
            "STDEV",
            "VAR",
            "COLLECT",
            "YEAR",
            "QUARTER",
            "MONTH",
            "WEEK",
            "DAY",
            "TRUNC_YEAR",
            "TRUNC_QUARTER",
            "TRUNC_MONTH",
            "TRUNC_WEEK",
            "TRUNC_DAY"
        ]
    },
    "MatchFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "description": "A Filter that can be used to match against String Fields",
                "properties": {
                    "contains": {
                        "type": "string",
                        "description": "Matches when a Field contains this value"
                    },
                    "startsWith": {
                        "type": "string",
                        "description": "Matches when a Field starts with this value"
                    },
                    "endsWith": {
                        "type": "string",
                        "description": "Matches when a Field ends with this value"
                    },
                    "exclude": {
                        "type": "boolean",
                        "description": "When true, the inverse of the matching logic will be used",
                        "default": False
                    }
                }
            }
        ]
    },
    "QuantitativeFilterBase": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "required": ["quantitativeFilterType"],
                "properties": {
                    "quantitativeFilterType": {
                        "type": "string",
                        "enum": [ "RANGE", "MIN", "MAX", "ONLY_NULL", "ONLY_NON_NULL" ]
                    },
                    "includeNulls": {
                        "type": "boolean",
                        "description": "Only applies to RANGE, MIN, and MAX Filters. Should nulls be returned or not. If not provided the default is to not include null values"
                    }
                }
            }
        ]
    },
    "QuantitativeNumericalFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/QuantitativeFilterBase"
            }
        ],
        "type": "object",
        "description": "A Filter that can be used to find the minimumn, maximumn or range of numerical values of a Field",
        "properties": {
            "min": {
                "type": "number",
                "description": "A numerical value, either integer or floating point indicating the minimum value to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            },
            "max": {
                "type": "number",
                "description": "A numerical value, either integer or floating point indicating the maximum value to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            }
        }
    },
    "QuantitativeDateFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/QuantitativeFilterBase"
            }
        ],
        "type": "object",
        "description": "A Filter that can be used to find the minimum, maximum or range of date values of a Field",
        "properties": {
            "minDate": {
                "type": "string",
                "format": "date",
                "description": "An RFC 3339 date indicating the earliest date to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            },
            "maxDate": {
                "type": "string",
                "format": "date",
                "description": "An RFC 3339 date indicating the latest date to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            }
        }
    },
    "Query": {
        "description": "The Query is the fundamental interface to Headless BI. It holds the specific semantics to perform against the Data Source. A Query consists of an array of Fields to query against, and an optional array of filters to apply to the query",
        "required": [
            "fields"
        ],
        "type": "object",
        "properties": {
            "fields": {
                "description": "An array of Fields that define the query",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Field"
                }
            },
            "filters": {
                "description": "An optional array of Filters to apply to the query",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Filter"
                }
            }
        },
        "additionalProperties": False
    },
    "SetFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            }
        ],
        "type": "object",
        "description": "A Filter that can be used to filter on a specific set of values of a Field",
        "required": [
            "values"
        ],
        "properties": {
            "values": {
                "type": "array",
                "items": {},
                "description": "An array of values to filter on"
            },
            "exclude": {
                "type": "boolean",
                "default": False
            }
        }
    },
    "SortDirection": {
        "type": "string",
        "description": "The direction of the sort, either ascending or descending. If not supplied the default is ascending",
        "enum": [
            "ASC",
            "DESC"
        ]
    },
    "RelativeDateFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "description": "A Filter that can be used to filter on dates using a specific anchor and fields that specify a relative date range to that anchor",
                "required": ["periodType", "dateRangeType"],
                "properties": {
                    "periodType": {
                        "type": "string",
                        "description": "The units of time in the relative date range",
                        "enum": [
                            "MINUTES",
                            "HOURS",
                            "DAYS",
                            "WEEKS",
                            "MONTHS",
                            "QUARTERS",
                            "YEARS"
                        ]
                    },
                    "dateRangeType": {
                        "type": "string",
                        "description": "The direction in the relative date range",
                        "enum": [
                            "CURRENT",
                            "LAST",
                            "LASTN",
                            "NEXT",
                            "NEXTN",
                            "TODATE"
                        ]
                    },
                    "rangeN": {
                        "type": "integer",
                        "description": "When dateRangeType is LASTN or NEXTN, this is the N value (how many years, months, etc.)."
                    },
                    "anchorDate": {
                        "type": "string",
                        "format": "date",
                        "description": "When this field is not provided, defaults to today."
                    },
                    "includeNulls": {
                        "type": "boolean",
                        "description": "Should nulls be returned or not. If not provided the default is to not include null values"
                    }
                }
            }
        ]
    },
    "TopNFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "description": "A Filter that can be used to find the top or bottom number of Fields relative to the values in the fieldToMeasure",
                "required": ["howMany, fieldToMeasure"],
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": [
                                "TOP",
                                "BOTTOM"
                            ],
                        "default": "TOP",
                        "description": "Top (Ascending) or Bottom (Descending) N"
                    },
                    "howMany": {
                        "type": "integer",
                        "description": "The number of values from the Top or the Bottom of the given fieldToMeasure"
                    },
                    "fieldToMeasure": {
                        "$ref": "#/components/schemas/FilterField"
                    }
                }
            }
        ]
    }
}

vds_few_shot = {
    "fields": {
        1: {
            "query": "Show me sales by segment",
            "JSON": {
                "fields": [
                {"fieldCaption": "Segment"},
                {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
            ]
            },
        },
        2: {
            "query": "What are the total sales and profit for each product category?",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Category"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2},
                    {"fieldCaption": "Profit", "function": "SUM", "maxDecimalPlaces": 2}
                ]
            },
        },
        3: {
            "query": "Display the number of orders by ship mode",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Ship Mode"},
                    {"fieldCaption": "Order ID", "function": "COUNT", "columnAlias": "Number of Orders"}
                ]
            },
        },
        4: {
            "query": "Show me the average sales per customer by segment",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Segment"},
                    {"fieldCaption": "Sales", "function": "AVG", "maxDecimalPlaces": 2, "columnAlias": "Average Sales per Customer"}
                ]
            },
        },
        5: {
            "query": "What are the total sales for each state or province?",
            "JSON": {
                "fields": [
                    {"fieldCaption": "State/Province"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ]
            },
        },
        6: {
            "query": "Average discount, total sales and profits by region sorted by profit",
            "JSON": {
                "fields": [
                    {
                        "fieldCaption": "Region"
                    },
                    {
                        "fieldCaption": "Discount",
                        "function": "AVG",
                        "maxDecimalPlaces": 2
                    },
                    {
                        "fieldCaption": "Sales",
                        "function": "SUM",
                        "maxDecimalPlaces": 2
                    },
                    {
                        "fieldCaption": "Profit",
                        "function": "SUM",
                        "maxDecimalPlaces": 2,
                        "sortPriority": 1,
                        "sortDirection": "DESC"
                    }
                ]
            }
        }
    },
    "filters": {
        1: {
            "query": "Show me sales for the top 10 cities",
            "JSON": {
                "fields": [
                    {"fieldCaption": "City"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ],
                "filters": [
                    {
                        "field": {
                            "fieldCaption": "Sales"
                        },
                        "filterType": "TOP",
                        "direction": "TOP",
                        "howMany": 10,
                        "fieldToMeasure": {"fieldCaption": "Sales", "function": "SUM"}
                    }
                ]
            }
        },
        2: {
            "query": "What are the sales for furniture products in the last 6 months?",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Product Name"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ],
                "filters": [
                    {
                        "field": {
                            "fieldCaption": "Category"
                    },
                        "filterType": "SET",
                        "values": ["Furniture"],
                        "exclude": False
                    },
                    {
                            "field": {
                            "fieldCaption": "Order Date"
                            },
                        "filterType": "DATE",
                        "periodtype": "MONTHS",
                        "dateRangeType": "LASTN",
                        "rangeN": 6
                    }
                ]
            }
        },
        3: {
            "query": "List customers who have made purchases over $1000 in the Consumer segment",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Customer Name"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ],
                "filters": [
                    {
                        "field": {
                            "fieldCaption": "Sales",
                        },
                        "filterType": "QUANTITATIVE_NUMERICAL",
                        "quantitativeFilterType": "MIN",
                        "min": 1000
                    },
                    {
                        "field": {
                            "fieldCaption": "Segment"
                        },
                        "filterType": "SET",
                        "values": ["Consumer"],
                        "exclude": False
                    }
                ]
            }
        },
        4: {
            "query": "Show me the orders that were returned in the West region",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Order ID"},
                    {"fieldCaption": "Product Name"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ],
                "filters": [
                    {
                        "field":
                        {
                            "fieldCaption": "Returned"
                        },
                        "filterType": "SET",
                        "values": [True],
                        "exclude": False
                    },
                    {
                        "field":
                        {
                            "fieldCaption": "Region"
                        },
                        "filterType": "SET",
                        "values": ["West"],
                        "exclude": False
                    }
                ]
            }
        },
        5: {
            "query": "What are the top 5 sub-categories by sales, excluding the Technology category?",
            "JSON": {
                "fields": [
                    {"fieldCaption": "Sub-Category"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ],
                "filters": [
                    {
                        "field":{
                            "fieldCaption": "Category"
                        },
                        "filterType": "SET",
                        "values": ["Technology"],
                        "exclude": True,
                    },
                    {
                        "field":{
                            "fieldCaption": "Sales"
                        },
                        "filterType": "TOP",
                        "direction": "TOP",
                        "howMany": 5,
                        "fieldToMeasure": {"fieldCaption": "Sales", "function": "SUM"}
                    }
                ]
            }
        },
        6: {
            "query": "Top selling sub-categories with a minimum of $200,000",
            "JSON": {
                "fields": [
                    {
                        "fieldCaption": "Sub-Category"
                    },
                    {
                        "fieldCaption": "Sales",
                        "function": "SUM",
                        "sortPriority": 1,
                        "sortDirection": "DESC"
                    }
                ],
                "filters": [
                    {
                        "field":{
                            "fieldCaption": "Sales"
                        },
                        "filterType": "QUANTITATIVE_NUMERICAL",
                        "quantitativeFilterType": "MIN",
                        "min": 200000
                        }
                ]
            }
        }
    },
    "calculations": {}
}

vds_prompt = {
    "instructions": vds_instructions,
    "restrictions": vds_restrictions,
    "vds_schema": vds_schema,
    "few_shot_examples": vds_few_shot,
    "data_model": {}
}

fields_instructions = f"""
Tasks:
- Your job is to write the main body of a request to Tableau’s VizQL Data Service (VDS) API to answer
  user questions with data and analytics.
- Query all useful or interesting fields even if additional transformations or calculations are needed.
- Always perform aggregations according to user needs to avoid returning too many rows of data.
- Include sorting as often as possible to highlight a field of interest in the query.
- Identify a List of filters that are categorical or of "STRING" type that would be used to filter the data
  at a later step

Restrictions:
- DO NOT HALLUCINATE FIELD NAMES
- Only use fields based on what is listed in the Data Source Metadata

The VDS query is a JSON object and to write it you must follow these steps:

1. Find the necessary `fieldCaptions` to write the query by checking the
   Data Source Metadata

2. Structure the overall payload or request body according to this spec:
   Query: \n{vds_schema.get('Query', None)}

3. Declare fields to query that help answer the user question following this spec:
   FieldBase: \n{vds_schema.get('FieldBase', None)}
   FieldMetadata: \n{vds_schema.get('FieldMetadata', None)}
   Field: \n{vds_schema.get('Field', None)}

4. Aggregate fields to match the granularity needed by the user per this spec:
   Function: \n{vds_schema.get('Function', None)}

5. Sort fields to prioritize display as specified by the user using this spec:
   SortDirection: \n{vds_schema.get('SortDirection', None)}

Few-shot Examples:
1. {{
    "query": "Average discount, total sales and profits by region sorted by profit",
    "JSON": {{
       "fields": [
           {{"fieldCaption": "Region"}},
           {{"fieldCaption": "Discount", "function": "AVG", "maxDecimalPlaces": 2}},
           {{"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}},
           {{"fieldCaption": "Profit", "function": "SUM", "maxDecimalPlaces": 2,
             "sortPriority": 1, "sortDirection": "DESC"}}
       ]
    }},
    "filter_fields": []
}}

2. {{
    "query": "Show me the average sales per customer by segment for Florida",
    "JSON": {{
       "fields": [
           {{"fieldCaption": "Segment"}},
           {{"fieldCaption": "Sales", "function": "AVG",
             "maxDecimalPlaces": 2, "columnAlias": "Average Sales per Customer"}}
       ]
    }},
    "filter_fields": ["State"]
}}

3. {{
    "query": "Display the number of orders by ship mode for the home office category in London",
    "JSON": {{
       "fields": [
           {{"fieldCaption": "Ship Mode"}},
           {{"fieldCaption": "Order ID",
             "function": "COUNT", "columnAlias": "Number of Orders"}}
       ]
    }},
    "filter_fields": ["Category", "City"]
}}

Output:
Your output must be in JSON and contain the following keys:
{{
    \"query\": \"The original user query to be used in the next step\",
    \"queried_fields_reasoning\": \"In 3 short sentences, describe your reasoning: why did you query these fields? Why did you aggregate & sort the data this way? How does this satisfy the user query?\",
    \"vds_payload\": \"The vds_payload with fields, aggregations, and sorts you wrote to satisfy the user query\",
    \"filter_fields\": \"List all relevant categorical or of "STRING" type fields that can be used as filters to answer the user query, the next step will generate these filters\"
}}

Data Source Metadata:
"""

filters_instructions = f"""
Task:
- Your job is to add filters to the main body of a request to Tableau's VDS API provided as the
input key `vds_payload` to answer user questions with data and analytics narrowed down to the
user's explicit specifications.

The VDS query is a JSON object, and to add filters to it you must follow these steps:

1. Understand the structure of a `vds_payload` input as described by this spec:
Query: {vds_schema.get('Query', 'No query provided')}

2. Deduce the necessary filter fields by checking the `data_model`, which only contains sample
filter values. You will need to make an educated guess to write the particular filter fields
needed by the user. The "categorical_filters" key contains filter values for STRING filters that
may contain the exact values you need to correctly filter the data

3. Select the right kind of filters to add to `vds_payload` to satisfy the needs of the user query,
considering the problem the user wants to solve:
- MatchFilter: {vds_schema.get('MatchFilter', 'No MatchFilter provided')}
- QuantitativeFilterBase: {vds_schema.get('QuantitativeFilterBase', 'No QuantitativeFilterBase provided')}
- QuantitativeNumericalFilter: {vds_schema.get('QuantitativeNumericalFilter', 'No QuantitativeNumericalFilter provided')}
- QuantitativeDateFilter: {vds_schema.get('QuantitativeDateFilter', 'No QuantitativeDateFilter provided')}
- SetFilter: {vds_schema.get('SetFilter', 'No SetFilter provided')}
- RelativeDateFilter: {vds_schema.get('RelativeDateFilter', 'No RelativeDateFilter provided')}
- TopNFilter: {vds_schema.get('TopNFilter', 'No TopNFilter provided')}

4. Add filter objects to `vds_payload` according to this spec:
Field: {vds_schema.get('Filter', 'No Filter provided')}
FilterField: {vds_schema.get('FilterField', 'No FilterField provided')}

Few-shot Examples:
1. "query": "Top selling sub-categories with a minimum of $200,000",
"JSON": {{
    "fields": [
        {{
            "fieldCaption": "Sub-Category"
        }},
        {{
            "fieldCaption": "Sales",
            "function": "SUM",
            "sortPriority": 1,
            "sortDirection": "DESC"
        }}
    ],
    "filters": [
        {{
            "field": {{
                "fieldCaption": "Sales"
            }},
            "filterType": "QUANTITATIVE_NUMERICAL",
            "quantitativeFilterType": "MIN",
            "min": 200000
        }}
    ]
}}
2. "query": "What are the sales for furniture products in the last 6 months?",
"JSON": {{
    "fields": [
        {{ "fieldCaption": "Product Name" }},
        {{ "fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2 }}
    ],
    "filters": [
        {{
            "field": {{ "fieldCaption": "Category" }},
            "filterType": "SET",
            "values": ["Furniture"],
            "exclude": false
        }},
        {{
            "field": {{ "fieldCaption": "Order Date" }},
            "filterType": "DATE",
            "periodtype": "MONTHS",
            "dateRangeType": "LASTN",
            "rangeN": 6
        }}
    ]
}}
3. "query": "What are the top 5 sub-categories by sales, excluding the Technology category?",
"JSON": {{
    "fields": [
        {{ "fieldCaption": "Sub-Category" }},
        {{ "fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2 }}
    ],
    "filters": [
        {{
            "field": {{
                "fieldCaption": "Category"
            }},
            "filterType": "SET",
            "values": ["Technology"],
            "exclude": true
        }},
        {{
            "field": {{
                "fieldCaption": "Sales"
            }},
            "filterType": "TOP",
            "direction": "TOP",
            "howMany": 5,
            "fieldToMeasure": {{
                "fieldCaption": "Sales",
                "function": "SUM"
            }}
        }}
    ]
}}

Output:
Your output must be in JSON and contain the following keys:
{{
    \"query\": \"The original user query to be used in the next step\",
    \"queried_fields_reasoning\": \"the verbatim contents of `queried_fields_reasoning` provided as an input key\",
    \"filtered_fields_reasoning\": \"in 3 short sentences, describe your reasoning: why did you filter these fields? why did you choose these types of filters?\",
    \"vds_payload\": \"the `vds_payload` provided as an input enhanced with the filters you wrote to satisfy the user query\"
}}
"""

calculations_instructions = f"""
Task:
- Your job is to add calculations to the main body of a request to Tableau's VDS API provided as the
input key `vds_payload` to answer user questions with data and analytics enhanced by analysis that does
not exist in the current data model.

The VDS query is a JSON object, and to add calculations to it you must follow these steps:

1. Understand the structure of a `vds_payload` input as described by this spec:
Query: {vds_schema.get('Query', 'No query provided')}

2. [Insert specific instructions here]

Few-shot Examples:
1. "query": "Top selling sub-categories with a minimum of $200,000"
"JSON": {{
    "fields": [
        {{
            "fieldCaption": "Sub-Category"
        }},
        {{
            "fieldCaption": "Sales",
            "function": "SUM",
            "sortPriority": 1,
            "sortDirection": "DESC"
        }}
    ],
    "filters": [
        {{
            "field": {{
                "fieldCaption": "Sales"
            }},
            "filterType": "QUANTITATIVE_NUMERICAL",
            "quantitativeFilterType": "MIN",
            "min": 200000
        }}
    ]
}}

Output:
Your output must be in JSON and contain 4 keys:
{{
    \"query\": \"The original user query to be used in the next step\",
    \"queried_fields_reasoning\": \"the verbatim contents of `queried_fields_reasoning` provided as an input key\",
    \"filtered_fields_reasoning\": \"the verbatim contents of `filtered_fields_reasoning` provided as an input key\",
    \"calculated_fields_reasoning\": \"In 3 short sentences, describe your reasoning: why did you write these calculations? How do they help the user answer the question or understand the problem?\",
    \"vds_payload\": \"the `vds_payload` provided as an input enhanced with the calculations you wrote to satisfy the user query\"
}}
"""

vds_prompts = {
    "fields_prompt": fields_instructions,
    "filters_prompt": filters_instructions,
    "calculations_prompt": calculations_instructions,
    "metadata_model": None,
    "categorical_filters": None
}
