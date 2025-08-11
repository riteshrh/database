"""
Configuration file for Snowflake Natural Language Query Application

Required Environment Variables:
1. OPENAI_API_KEY - Your OpenAI API key
2. SNOWFLAKE_USER - Snowflake username
3. SNOWFLAKE_PASSWORD - Snowflake password
4. SNOWFLAKE_ACCOUNT - Snowflake account identifier
5. SNOWFLAKE_WAREHOUSE - Snowflake warehouse name
6. SNOWFLAKE_DATABASE - Snowflake database name (default: userprofiles)
7. SNOWFLAKE_SCHEMA - Snowflake schema name (default: public)

Create a .env file in your project root with these variables:
"""

ENV_TEMPLATE = """
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Snowflake Database Configuration
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account_identifier
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=userprofiles
SNOWFLAKE_SCHEMA=public
"""

# Default configuration values
DEFAULT_CONFIG = {
    "SNOWFLAKE_DATABASE": "userprofiles",
    "SNOWFLAKE_SCHEMA": "public"
}

if __name__ == "__main__":
    print("Environment Variables Template:")
    print(ENV_TEMPLATE)
    print("\nMake sure to create a .env file with your actual values!") 