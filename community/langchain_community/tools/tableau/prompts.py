vds_instructions = """
You are an expert at writing API request bodies for Tableau’s HeadlessBI API.
The HBI query is a JSON object that contains 2 fundamental components.
    1. fields [required] - an array of fields that define the desired output of the query
    2. filters [optional] - an array of filters to apply to the query. They can include fields that are not in the fields array.
Your task is to retrieve data relevant to a user’s natural language query.

Query as much data as might be useful; it's ok if you pull in superfluous fields,
You will be successful if you bring back all the data that could help to answer the question, even if additional transformation and actions are needed.

You can find the fieldCaptions by checking the data_model field.
Keep your output very structured. Use the following structure:
Reasoning:

JSON_payload:
Make sure you use this structure so that it's simple to parse the output.
Return query results verbatim
"""

vds_restrictions = """
DO NOT HALLUCINATE FIELD NAMES.
Don't try to do too much with the json query.
Only use fields based on what is listed in the data_model
Do not filter or reduce any data found in query results so the next link can determine future steps.
"""

vds_few_shot = {
    "superstore": {
        "columns": {
            1: {
                "query": "Show me sales by segment",
                "JSON": {
                    "columns": [
                    {"columnName": "Segment"},
                    {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ]
                },
            },
            2: {
                "query": "What are the total sales and profit for each product category?",
                "JSON": {
                    "columns": [
                        {"columnName": "Category"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2},
                        {"columnName": "Profit", "function": "SUM", "maxDecimalPlaces": 2}
                    ]
                },
            },
            3: {
                "query": "Display the number of orders by ship mode",
                "JSON": {
                    "columns": [
                        {"columnName": "Ship Mode"},
                        {"columnName": "Order ID", "function": "COUNT", "columnAlias": "Number of Orders"}
                    ]
                },
            },
            4: {
                "query": "Show me the average sales per customer by segment",
                "JSON": {
                    "columns": [
                        {"columnName": "Segment"},
                        {"columnName": "Sales", "function": "AVG", "maxDecimalPlaces": 2, "columnAlias": "Average Sales per Customer"}
                    ]
                },
            },
            5: {
                "query": "What are the total sales for each state or province?",
                "JSON": {
                    "columns": [
                        {"columnName": "State/Province"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ]
                },
            },
        },
        "filters": {
            1: {
                "query": "Show me sales for the top 10 cities",
                "JSON": {
                    "columns": [
                        {"columnName": "City"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Sales",
                            "filterType": "TOP",
                            "direction": "TOP",
                            "howMany": 10,
                            "fieldToMeasure": {"columnName": "Sales", "function": "SUM"}
                        }
                    ]
                }
            },
            2: {
                "query": "What are the sales for furniture products in the last 6 months?",
                "JSON": {
                    "columns": [
                        {"columnName": "Product Name"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Category",
                            "filterType": "SET",
                            "values": ["Furniture"],
                            "exclude": False
                        },
                        {
                            "columnName": "Order Date",
                            "filterType": "DATE",
                            "units": "MONTHS",
                            "pastCount": 6
                        }
                    ]
                }
            },
            3: {
                "query": "List customers who have made purchases over $1000 in the Consumer segment",
                "JSON": {
                    "columns": [
                        {"columnName": "Customer Name"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Sales",
                            "filterType": "QUANTITATIVE",
                            "quantitativeFilterType": "MIN",
                            "min": 1000
                        },
                        {
                            "columnName": "Segment",
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
                    "columns": [
                        {"columnName": "Order ID"},
                        {"columnName": "Product Name"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Returned",
                            "filterType": "SET",
                            "values": [True],
                            "exclude": False
                        },
                        {
                            "columnName": "Region",
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
                    "columns": [
                        {"columnName": "Sub-Category"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Category",
                            "filterType": "SET",
                            "values": ["Technology"],
                            "exclude": True,
                        },
                        {
                            "columnName": "Sales",
                            "filterType": "TOP",
                            "direction": "TOP",
                            "howMany": 5,
                            "fieldToMeasure": {"columnName": "Sales", "function": "SUM"}
                        }
                    ]
                }
            },
            6: {
                "query": "Top selling sub-categories with a minimum of $200,000",
                "JSON": {
                    "columns": [
                        {"columnName": "Sub-Category"},
                        {"columnName": "Sales", "function": "SUM", "sortPriority": 1, "sortDirection": "DESC"}
                    ],
                    "filters": [
                        {"columnName": "Sales", "filterType": "QUANTITATIVE", "quantitativeFilterType": "MIN", "min": 200000}
                    ]
                }
            }
        },
        "calculations": {},
    }
}

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
},

vds_prompt = {
    "instructions": vds_instructions,
    "restrictions": vds_restrictions,
    "data_model": {},
    "vds_schema": vds_schema,
    "few_shot_examples": None
}
