import streamlit as st
import pandas as pd
import snowflake.connector
import openai
import os
from dotenv import load_dotenv
import io
from nurse_practitioner_search import NursePractitionerSearch

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Snowflake Natural Language Query & NP Search",
    page_icon="❄️🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client
try:
    # Try Streamlit secrets first (for deployed apps)
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        # Fallback to environment variables (for local development)
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.error("❌ OPENAI_API_KEY not found!")
        st.info("💡 **Local Development**: Add to .env file | **Streamlit Cloud**: Add to Settings → Secrets")
        st.stop()
    
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"❌ Error initializing OpenAI client: {str(e)}")
    st.info("💡 **Local Development**: Add to .env file | **Streamlit Cloud**: Add to Settings → Secrets")
    st.stop()

# Snowflake connection configuration
try:
    # Try Streamlit secrets first (for deployed apps)
    SNOWFLAKE_CONFIG = {
        "user": st.secrets.get("SNOWFLAKE_USER") or os.getenv("SNOWFLAKE_USER"),
        "password": st.secrets.get("SNOWFLAKE_PASSWORD") or os.getenv("SNOWFLAKE_PASSWORD"),
        "account": st.secrets.get("SNOWFLAKE_ACCOUNT") or os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": st.secrets.get("SNOWFLAKE_WAREHOUSE") or os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": st.secrets.get("SNOWFLAKE_DATABASE") or os.getenv("SNOWFLAKE_DATABASE"),
        "schema": st.secrets.get("SNOWFLAKE_SCHEMA") or os.getenv("SNOWFLAKE_SCHEMA")
    }
    
    # Check if any required values are missing
    missing_values = [key for key, value in SNOWFLAKE_CONFIG.items() if not value]
    if missing_values:
        st.error(f"❌ Missing Snowflake configuration: {', '.join(missing_values)}")
        st.info("💡 **Local Development**: Add to .env file | **Streamlit Cloud**: Add to Settings → Secrets")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Error loading Snowflake configuration: {str(e)}")
    st.info("💡 **Local Development**: Add to .env file | **Streamlit Cloud**: Add to Settings → Secrets")
    st.stop()

# Database schema information for context
DATABASE_SCHEMA = """
Tables available:

1. userprofiles.public.contact_search_dz (alias: c)
   - Contact information: FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, EMAIL_STATUS
   - Job details: JOB_TITLE, JOB_FUNCTION, JOB_DESCRIPTION, JOB_LEVEL, JOB_START_DATE, JOB_END_DATE, JOB_IS_CURRENT
   - Location: JOB_LOCATION_CITY, JOB_LOCATION_STATE, JOB_LOCATION_STATE_CODE, JOB_LOCATION_COUNTRY, JOB_LOCATION_COUNTRY_CODE
   - Company: COMPANY_NAME, COMPANY_URL, RBID_ORG, RBID
   - Skills & Education: SKILLS, EDUCATION
   - LinkedIn: LINKEDIN_URL, LINKEDIN_HEADLINE, LINKEDIN_CONNECTIONS_COUNT, LINKEDIN_INDUSTRY

2. userprofiles.public.org_latest_copy (alias: o)
   - Company info: COMPANY_NAME, ABOUT_US, EMPLOYEE_COUNT_MIN, EMPLOYEE_COUNT_MAX
   - Industry: INDUSTRY_LINKEDIN, INDUSTRY_SIC_CODE, INDUSTRY_NAICS_CODE
   - Location: HEADQUARTERS_CITY, HEADQUARTERS_STATE_CODE, HEADQUARTERS_COUNTRY_CODE
   - Contact: PHONE, WEBSITE, DOMAIN

3. userprofiles.public.per_latest_copy (alias: p)
   - Profile: FIRST_NAME, LAST_NAME, FULL_NAME, ABOUT_ME
   - Contact: EMAIL_ADDRESS, CELLPHONE, DIRECT_PHONE
   - Location: CITY, STATE_CODE, COUNTRY_CODE
   - Job: JOB_TITLE, JOB_DESCRIPTION, JOB_LEVEL, JOB_FUNCTION
   - Skills: SKILLS, CERTIFICATIONS, EDUCATION, LANGUAGES, INTERESTS
   - LinkedIn: LINKEDIN_URL, LINKEDIN_HEADLINE, LINKEDIN_CONNECTIONS_COUNT

IMPORTANT: Use the correct table aliases and column names. Do NOT reference columns that don't exist in the specified table.
"""

def get_snowflake_connection():
    """Create and return a Snowflake connection"""
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {str(e)}")
        return None

def natural_language_to_sql(natural_query):
    """Convert natural language to SQL using OpenAI"""
    
    system_prompt = f"""You are a SQL expert specializing in Snowflake SQL. Convert the user's natural language query into valid Snowflake SQL.

Database Schema:
{DATABASE_SCHEMA}

CRITICAL RULES:
1. Use proper Snowflake SQL syntax
2. ALWAYS use the correct table aliases: 'c' for contact_search_dz, 'o' for org_latest_copy, 'p' for per_latest_copy
3. ONLY reference columns that actually exist in the specified tables
4. For nurse practitioner searches, be CREATIVE and FLEXIBLE:
   - Use flexible job title matching: LOWER(c.JOB_TITLE) LIKE ANY ('%nurse%', '%np%', '%nurse practitioner%', '%rn%', '%registered nurse%', '%advanced practice%', '%apn%', '%fnp%', '%anp%', '%pnp%', '%pmhnp%')
   - Check MULTIPLE fields for telehealth experience: c.JOB_DESCRIPTION, c.LINKEDIN_HEADLINE, c.SKILLS, c.EDUCATION
   - Use creative telehealth keywords: 'telehealth', 'telemedicine', 'remote', 'virtual', 'online', 'telepractice', 'e-health', 'digital health', 'remote care', 'virtual care', 'teleconsultation', 'telemonitoring'
   - Consider alternative spellings and variations
5. For state licensing, use c.JOB_LOCATION_STATE_CODE and be flexible with state formats
6. Always use proper table aliases and JOIN syntax when combining tables
7. IMPORTANT: When using GROUP BY with COUNT(DISTINCT), only ORDER BY columns that are in the GROUP BY clause or use aggregate functions
8. IMPORTANT: Use proper LIKE syntax - '%keyword%' NOT '%%keyword%%' or '%keyword%'
9. Return only the SQL query, no explanations

CREATIVE NURSE PRACTITIONER SEARCH STRATEGIES:
- Look for nurse-related job titles in c.JOB_TITLE
- Check c.JOB_DESCRIPTION for telehealth experience
- Check c.LINKEDIN_HEADLINE for telehealth keywords
- Check c.SKILLS for telehealth-related skills
- Check c.EDUCATION for nursing degrees or telehealth certifications
- Use OR conditions to catch telehealth experience in any of these fields
- Consider partial matches and variations

Example nurse practitioner query:
"Find nurse practitioners licensed in California and Texas with telehealth experience"
Should generate SQL like:
SELECT c.FIRST_NAME, c.LAST_NAME, c.JOB_TITLE, c.JOB_DESCRIPTION, c.LINKEDIN_HEADLINE, c.SKILLS, c.EDUCATION, c.JOB_LOCATION_STATE_CODE, c.COMPANY_NAME
FROM userprofiles.public.contact_search_dz c
WHERE (
    LOWER(c.JOB_TITLE) LIKE ANY ('%nurse%', '%np%', '%nurse practitioner%', '%rn%', '%registered nurse%', '%advanced practice%', '%apn%', '%fnp%', '%anp%', '%pnp%', '%pmhnp%')
    OR LOWER(c.JOB_FUNCTION) LIKE '%nurse%'
)
AND c.JOB_LOCATION_STATE_CODE IN ('CA', 'TX')
AND (
    LOWER(COALESCE(c.JOB_DESCRIPTION, '')) LIKE ANY ('%telehealth%', '%telemedicine%', '%remote%', '%virtual%', '%online%', '%telepractice%', '%e-health%', '%digital health%', '%remote care%', '%virtual care%')
    OR LOWER(COALESCE(c.LINKEDIN_HEADLINE, '')) LIKE ANY ('%telehealth%', '%telemedicine%', '%remote%', '%virtual%', '%online%', '%telepractice%', '%e-health%', '%digital health%', '%remote care%', '%virtual care%')
    OR LOWER(COALESCE(c.SKILLS, '')) LIKE ANY ('%telehealth%', '%telemedicine%', '%remote%', '%virtual%', '%online%', '%telepractice%', '%e-health%', '%digital health%', '%remote care%', '%virtual care%')
    OR LOWER(COALESCE(c.EDUCATION, '')) LIKE ANY ('%telehealth%', '%telemedicine%', '%remote%', '%virtual%', '%online%', '%telepractice%', '%e-health%', '%digital health%', '%remote care%', '%virtual care%')
)
AND COALESCE(c.JOB_IS_CURRENT, FALSE) = TRUE
ORDER BY c.JOB_START_DATE DESC

For multi-state licensing queries, use this pattern:
SELECT c.FIRST_NAME, c.LAST_NAME, c.JOB_TITLE, c.JOB_DESCRIPTION, c.LINKEDIN_HEADLINE, c.SKILLS, c.EDUCATION, c.COMPANY_NAME, COUNT(DISTINCT c.JOB_LOCATION_STATE_CODE) AS LICENSED_STATES
FROM userprofiles.public.contact_search_dz c
WHERE [nurse and telehealth conditions]
GROUP BY c.FIRST_NAME, c.LAST_NAME, c.JOB_TITLE, c.JOB_DESCRIPTION, c.LINKEDIN_HEADLINE, c.SKILLS, c.EDUCATION, c.COMPANY_NAME
HAVING COUNT(DISTINCT c.JOB_LOCATION_STATE_CODE) >= [number]
ORDER BY LICENSED_STATES DESC, c.FIRST_NAME, c.LAST_NAME

IMPORTANT: Always use clean LIKE patterns like '%keyword%' and avoid double quotes or malformed patterns.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_query}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the response to extract just the SQL
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        return sql_query.strip()
    
    except Exception as e:
        st.error(f"Error generating SQL: {str(e)}")
        return None

def execute_sql_query(sql_query):
    """Execute SQL query and return results"""
    conn = get_snowflake_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Fetch results
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=column_names)
        
        # Fix data type issues for Streamlit display
        df = fix_dataframe_for_streamlit(df)
        
        cursor.close()
        conn.close()
        
        return df
    
    except Exception as e:
        st.error(f"Error executing SQL: {str(e)}")
        if conn:
            conn.close()
        return None

def fix_dataframe_for_streamlit(df):
    """Fix dataframe data types to be compatible with Streamlit and PyArrow"""
    
    # Convert problematic data types
    for col in df.columns:
        # Handle object/string columns that might cause PyArrow issues
        if df[col].dtype == 'object':
            # Convert to string, handling None/NaN values
            df[col] = df[col].astype(str).replace('nan', '').replace('None', '')
        
        # Handle datetime columns
        elif 'datetime' in str(df[col].dtype):
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Handle numeric columns with mixed types
        elif df[col].dtype == 'object':
            try:
                # Try to convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                # If conversion fails, keep as string
                df[col] = df[col].astype(str).replace('nan', '').replace('None', '')
    
    return df

def validate_sql_query(sql_query):
    """Basic SQL validation"""
    # Check for dangerous keywords
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
    sql_upper = sql_query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Query contains potentially dangerous keyword: {keyword}"
    
    # Check for SELECT statement
    if 'SELECT' not in sql_upper:
        return False, "Query must contain a SELECT statement"
    
    return True, "Query appears safe"

def show_general_query_interface():
    """Show the general natural language to SQL interface"""
    
    st.subheader("🔍 General Natural Language Query")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        natural_query = st.text_area(
            "Describe what you want to find:",
            value=st.session_state.get('natural_query', ''),
            height=150,
            placeholder="e.g., Find nurse practitioners licensed in California and Texas with telehealth experience"
        )
        
        if st.button("🚀 Convert to SQL", type="primary"):
            if natural_query.strip():
                with st.spinner("Converting to SQL..."):
                    sql_query = natural_language_to_sql(natural_query)
                    if sql_query:
                        st.session_state.generated_sql = sql_query
                        st.success("SQL generated successfully!")
            else:
                st.warning("Please enter a natural language query")
    
    with col2:
        st.subheader("Generated SQL")
        if 'generated_sql' in st.session_state:
            sql_query = st.session_state.generated_sql
            
            # Display the SQL with syntax highlighting
            st.code(sql_query, language="sql")
            
            # SQL validation
            is_valid, validation_message = validate_sql_query(sql_query)
            
            if is_valid:
                st.success(validation_message)
                
                if st.button("🔍 Execute Query", type="secondary"):
                    with st.spinner("Executing query..."):
                        results_df = execute_sql_query(sql_query)
                        
                        if results_df is not None:
                            st.session_state.query_results = results_df
                            st.success(f"Query executed successfully! Found {len(results_df)} results.")
                        else:
                            st.error("Failed to execute query")
            else:
                st.error(validation_message)
                st.warning("Please review and fix the SQL query before execution")

def show_results_analysis():
    """Show the results analysis section"""
    
    if 'query_results' in st.session_state and st.session_state.query_results is not None:
        st.markdown("---")
        st.subheader("📊 Query Results")
        
        results_df = st.session_state.query_results
        
        # Display results info
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Total Rows", len(results_df))
        with col_info2:
            st.metric("Total Columns", len(results_df.columns))
        with col_info3:
            st.metric("Memory Usage", f"{results_df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # Display the dataframe
        st.dataframe(results_df, use_container_width=True)
        
        # Download options
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            try:
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"❌ CSV download failed: {str(e)}")
                st.info("💡 The data may contain unsupported characters.")
        
        with col_dl2:
            excel_buffer = io.BytesIO()
            try:
                # Clean data for Excel export
                cleaned_df = clean_data_for_excel(results_df)
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    cleaned_df.to_excel(writer, index=False, sheet_name='Query Results')
                excel_data = excel_buffer.getvalue()
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="query_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"❌ Excel export failed: {str(e)}")
                st.info("💡 Try downloading as CSV instead, or the data may contain unsupported characters.")
                # Fallback to CSV
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV (Fallback)",
                    data=csv_data,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
        
        # Show sample data analysis
        st.subheader("Data Preview")
        tab1, tab2, tab3 = st.tabs(["First 10 Rows", "Data Types", "Missing Values"])
        
        with tab1:
            st.dataframe(results_df.head(10), use_container_width=True)
        
        with tab2:
            st.dataframe(results_df.dtypes.to_frame('Data Type'), use_container_width=True)
        
        with tab3:
            missing_data = results_df.isnull().sum().to_frame('Missing Count')
            missing_data['Missing Percentage'] = (missing_data['Missing Count'] / len(results_df)) * 100
            st.dataframe(missing_data, use_container_width=True)

def clean_data_for_excel(df):
    """Clean dataframe data to make it Excel-compatible"""
    cleaned_df = df.copy()
    
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            # Replace illegal characters that cause Excel export errors
            cleaned_df[col] = cleaned_df[col].astype(str).apply(
                lambda x: x.replace('~', '-').replace('`', "'").replace('|', '-') if pd.notna(x) else x
            )
            # Truncate very long strings to avoid Excel cell limits
            cleaned_df[col] = cleaned_df[col].apply(
                lambda x: x[:32000] + '...' if pd.notna(x) and len(str(x)) > 32000 else x
            )
    
    return cleaned_df

def main():
    st.title("❄️🏥 GradToHired Database Automation")
    st.markdown("Convert natural language to SQL and find specialized healthcare professionals")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        
        # Choose the main interface
        interface_choice = st.radio(
            "Choose Interface:",
            ["General Query", "Nurse Practitioner Search"],
            help="Select which interface to use"
        )
        
        st.markdown("---")
        
        # Example queries for general interface
        if interface_choice == "General Query":
            st.subheader("Example Queries")
            example_queries = [
                "Find nurse practitioners licensed in California and Texas with telehealth experience",
                "Show all software engineers with Python skills in San Francisco",
                "Find companies in the healthcare industry with more than 1000 employees",
                "Show people with nursing degrees and certifications in multiple states"
            ]
            
            for i, query in enumerate(example_queries):
                if st.button(f"Example {i+1}", key=f"example_{i}"):
                    st.session_state.natural_query = query
        
        st.markdown("---")
        st.markdown("**Database Tables:**")
        st.markdown("- `contact_search_dz` - Contact & job info")
        st.markdown("- `org_latest_copy` - Company data")
        st.markdown("- `per_latest_copy` - Person profiles")
    
    # Main content area
    st.markdown("---")
    
    if interface_choice == "General Query":
        show_general_query_interface()
        show_results_analysis()
    
    elif interface_choice == "Nurse Practitioner Search":
        st.subheader("🏥 Specialized Nurse Practitioner Search")
        st.markdown("""
        This specialized interface helps you find nurse practitioners with specific requirements:
        - **Multi-state licensing**: Find NPs licensed in multiple states
        - **Telehealth experience**: Identify candidates with remote care experience
        - **Advanced filtering**: Refine searches by location, company, and skills
        """)
        
        # Initialize the nurse practitioner search
        try:
            np_search = NursePractitionerSearch()
            st.success("✅ Nurse Practitioner Search module initialized successfully!")
            
            # Show the advanced search UI
            results = np_search.get_advanced_search_ui()
            
            # If we have results, analyze them
            if results is not None and not results.empty:
                st.success(f"🎯 Found {len(results)} candidates!")
                np_search.analyze_results(results)
            elif results is not None:
                st.info("ℹ️ No results found. Try adjusting your search criteria.")
            else:
                st.info("ℹ️ Search interface loaded. Enter your criteria above to search.")
                
        except Exception as e:
            st.error(f"❌ Failed to initialize Nurse Practitioner Search: {str(e)}")
            st.info("💡 Check your configuration and try again.")
            
            # Show detailed error information
            with st.expander("🐛 Error Details", expanded=True):
                st.code(f"Error Type: {type(e).__name__}")
                st.code(f"Error Message: {str(e)}")
                st.code(f"Error Location: {e.__traceback__.tb_frame.f_code.co_name}")
                
            # Show troubleshooting steps
            st.markdown("### 🔧 Troubleshooting Steps:")
            st.markdown("1. **Check Configuration**: Ensure all environment variables are set")
            st.markdown("2. **Verify Secrets**: In Streamlit Cloud, go to Settings → Secrets")
            st.markdown("3. **Check Logs**: Look for detailed error messages")
            st.markdown("4. **Test Connection**: Try the General Query interface first")
    
    else:
        st.error(f"❌ Unknown interface choice: {interface_choice}")
        st.info("💡 Please select either 'General Query' or 'Nurse Practitioner Search' from the sidebar.")

if __name__ == "__main__":
    main() 