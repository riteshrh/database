"""
Specialized Nurse Practitioner Search Module

This module provides optimized search functionality for finding nurse practitioners
with specific licensing requirements and telehealth experience.
"""

import streamlit as st
import pandas as pd
import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

class NursePractitionerSearch:
    """Specialized class for nurse practitioner searches"""
    
    def __init__(self):
        # Check for required environment variables
        required_vars = [
            "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT", 
            "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            st.info("💡 If deploying on Streamlit Cloud, go to Settings → Secrets and add your Snowflake credentials.")
            st.stop()
        
        self.snowflake_config = {
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA")
        }
        
        # Common nurse practitioner job titles and variations
        self.nurse_titles = [
            'nurse practitioner', 'np', 'nurse', 'rn', 'registered nurse',
            'advanced practice nurse', 'apn', 'family nurse practitioner',
            'fnp', 'adult nurse practitioner', 'anp', 'pediatric nurse practitioner',
            'pnp', 'psychiatric nurse practitioner', 'pmhnp', 'clinical nurse specialist',
            'cns', 'nurse anesthetist', 'crna', 'nurse midwife', 'cnm',
            'acute care nurse practitioner', 'acnp', 'geriatric nurse practitioner', 'gnp'
        ]
        
        # Enhanced telehealth-related keywords with variations
        self.telehealth_keywords = [
            'telehealth', 'telemedicine', 'remote', 'virtual', 'online',
            'telepractice', 'ehealth', 'digital health', 'remote care',
            'virtual care', 'teleconsultation', 'telemonitoring',
            'telemed', 'telenursing', 'telepsychiatry', 'telecardiology',
            'remote patient monitoring', 'virtual visits', 'online consultations',
            'digital consultations', 'remote healthcare', 'virtual healthcare',
            'telehealth platform', 'telemedicine platform', 'remote clinical',
            'virtual clinical', 'online clinical', 'digital clinical'
        ]
        
        # State abbreviations for licensing
        self.state_abbreviations = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT',
            'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI',
            'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
            'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME',
            'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI',
            'minnesota': 'MN', 'mississippi': 'MS', 'missouri': 'MO',
            'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM',
            'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND',
            'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA',
            'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD',
            'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT', 'vermont': 'VT',
            'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
    
    def get_connection(self):
        """Get Snowflake connection"""
        try:
            return snowflake.connector.connect(**self.snowflake_config)
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            return None
    
    def search_nurse_practitioners(self, states, min_states=1, require_telehealth=True):
        """
        Search for nurse practitioners licensed in specified states with telehealth experience
        
        Args:
            states (list): List of state names or abbreviations
            min_states (int): Minimum number of states required
            require_telehealth (bool): Whether to require telehealth experience
        
        Returns:
            pd.DataFrame: Search results
        """
        
        # Convert state names to abbreviations
        state_codes = []
        for state in states:
            state_lower = state.lower().strip()
            if state_lower in self.state_abbreviations:
                state_codes.append(self.state_abbreviations[state_lower])
            elif state_lower.upper() in self.state_abbreviations.values():
                state_codes.append(state_lower.upper())
        
        if not state_codes:
            st.error("No valid states provided")
            return None
        
        # Build the SQL query
        sql_query = self._build_np_search_query(state_codes, min_states, require_telehealth)
        
        # Execute the query
        return self._execute_query(sql_query)
    
    def _build_np_search_query(self, state_codes, min_states, require_telehealth):
        """Build the SQL query for nurse practitioner search"""
        
        # Create clean keyword lists for SQL
        telehealth_patterns = [f"'%{keyword}%'" for keyword in self.telehealth_keywords]
        nurse_patterns = [f"'%{title}%'" for title in self.nurse_titles]
        
        # Base query focusing on contact_search_dz table with creative telehealth detection
        base_query = f"""
        WITH nurse_candidates AS (
            SELECT 
                c.FIRST_NAME,
                c.LAST_NAME,
                c.EMAIL_ADDRESS,
                c.JOB_TITLE,
                c.JOB_DESCRIPTION,
                c.LINKEDIN_HEADLINE,
                c.JOB_LOCATION_CITY,
                c.JOB_LOCATION_STATE,
                c.JOB_LOCATION_STATE_CODE,
                c.COMPANY_NAME,
                c.SKILLS,
                c.EDUCATION,
                c.LINKEDIN_URL,
                c.JOB_FUNCTION,
                c.JOB_LEVEL,
                c.JOB_START_DATE,
                c.JOB_END_DATE,
                c.JOB_IS_CURRENT,
                c.JOB_ORG_LINKEDIN_URL,
                c.JOB_ORDER_IN_PROFILE,
                c.JOB_LOCATION_COUNTRY,
                c.JOB_LOCATION_COUNTRY_CODE,
                c.JOB_LOCATION_COUNTRY_REGION,
                c.JOB_LOCATION_CONTINENT,
                c.COUNTRY_NAME,
                c.STATE_NAME,
                c.JOB_COUNT,
                c.COMPANY_URL,
                c.RBID_ORG,
                c.RBID,
                c.COMPANY_PREFIX,
                c.JOBTITLE_PREFIX,
                -- Count distinct states where they have job locations
                COUNT(DISTINCT c.JOB_LOCATION_STATE_CODE) as states_licensed_in,
                -- Enhanced telehealth experience detection across multiple fields
                CASE 
                    WHEN (
                        LOWER(COALESCE(c.JOB_DESCRIPTION, '')) LIKE ANY ({', '.join(telehealth_patterns)})
                        OR LOWER(COALESCE(c.LINKEDIN_HEADLINE, '')) LIKE ANY ({', '.join(telehealth_patterns)})
                        OR LOWER(COALESCE(c.SKILLS, '')) LIKE ANY ({', '.join(telehealth_patterns)})
                        OR LOWER(COALESCE(c.EDUCATION, '')) LIKE ANY ({', '.join(telehealth_patterns)})
                        OR LOWER(COALESCE(c.JOB_FUNCTION, '')) LIKE ANY ({', '.join(telehealth_patterns)})
                    ) THEN TRUE 
                    ELSE FALSE 
                END as has_telehealth_experience,
                -- Enhanced nurse title detection
                CASE 
                    WHEN LOWER(COALESCE(c.JOB_TITLE, '')) LIKE ANY ({', '.join(nurse_patterns)})
                    OR LOWER(COALESCE(c.JOB_FUNCTION, '')) LIKE ANY ({', '.join(nurse_patterns)})
                    THEN TRUE 
                    ELSE FALSE 
                END as is_nurse_practitioner
            FROM userprofiles.public.contact_search_dz c
            WHERE 
                -- Enhanced nurse practitioner detection
                (
                    LOWER(COALESCE(c.JOB_TITLE, '')) LIKE ANY ({', '.join(nurse_patterns)})
                    OR LOWER(COALESCE(c.JOB_FUNCTION, '')) LIKE ANY ({', '.join(nurse_patterns)})
                    OR LOWER(COALESCE(c.JOB_DESCRIPTION, '')) LIKE ANY ({', '.join(nurse_patterns)})
                )
                -- Check if they have locations in any of the specified states
                AND c.JOB_LOCATION_STATE_CODE IN ({', '.join([f"'{code}'" for code in state_codes])})
                -- Only include current jobs
                AND COALESCE(c.JOB_IS_CURRENT, FALSE) = TRUE
            GROUP BY 
                c.FIRST_NAME, c.LAST_NAME, c.EMAIL_ADDRESS, c.JOB_TITLE, 
                c.JOB_DESCRIPTION, c.LINKEDIN_HEADLINE, c.JOB_LOCATION_STATE_CODE,
                c.JOB_LOCATION_CITY, c.JOB_LOCATION_STATE, c.JOB_LOCATION_COUNTRY,
                c.COMPANY_NAME, c.SKILLS, c.EDUCATION, c.LINKEDIN_URL,
                c.JOB_FUNCTION, c.JOB_LEVEL, c.JOB_START_DATE, c.JOB_END_DATE,
                c.JOB_IS_CURRENT, c.JOB_ORG_LINKEDIN_URL, c.JOB_ORDER_IN_PROFILE,
                c.JOB_LOCATION_STATE_CODE, c.JOB_LOCATION_COUNTRY_CODE,
                c.JOB_LOCATION_COUNTRY_REGION, c.JOB_LOCATION_CONTINENT,
                c.COUNTRY_NAME, c.STATE_NAME, c.JOB_COUNT, c.COMPANY_URL,
                c.RBID_ORG, c.RBID, c.COMPANY_PREFIX, c.JOBTITLE_PREFIX
        )
        SELECT 
            FIRST_NAME,
            LAST_NAME,
            EMAIL_ADDRESS,
            JOB_TITLE,
            JOB_DESCRIPTION,
            LINKEDIN_HEADLINE,
            JOB_LOCATION_CITY,
            JOB_LOCATION_STATE,
            JOB_LOCATION_STATE_CODE,
            COMPANY_NAME,
            SKILLS,
            EDUCATION,
            LINKEDIN_URL,
            states_licensed_in,
            has_telehealth_experience,
            is_nurse_practitioner,
            JOB_START_DATE,
            JOB_END_DATE,
            JOB_IS_CURRENT
        FROM nurse_candidates
        WHERE 
            states_licensed_in >= {min_states}
            AND is_nurse_practitioner = TRUE
            {f"AND has_telehealth_experience = TRUE" if require_telehealth else ""}
        ORDER BY 
            states_licensed_in DESC,
            has_telehealth_experience DESC,
            JOB_START_DATE DESC
        """
        
        return base_query
    
    def _execute_query(self, sql_query):
        """Execute SQL query and return results"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            df = pd.DataFrame(results, columns=column_names)
            
            cursor.close()
            conn.close()
            
            return df
        
        except Exception as e:
            st.error(f"Query execution failed: {str(e)}")
            if conn:
                conn.close()
            return None
    
    def get_advanced_search_ui(self):
        """Create an advanced search UI for nurse practitioners"""
        
        st.subheader("🔍 Advanced Nurse Practitioner Search")
        
        # Creative search options
        with st.expander("🎯 Creative Search Options", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Nurse Title Matching:**")
                custom_nurse_titles = st.text_area(
                    "Custom nurse titles (one per line):",
                    value="\n".join(self.nurse_titles[:10]),  # Show first 10 as examples
                    height=100,
                    help="Add custom nurse practitioner job titles to search for"
                )
                
                # Update nurse titles if custom ones provided
                if custom_nurse_titles.strip():
                    custom_titles = [title.strip() for title in custom_nurse_titles.split('\n') if title.strip()]
                    if custom_titles:
                        self.nurse_titles = custom_titles
            
            with col2:
                st.write("**Telehealth Keywords:**")
                custom_telehealth = st.text_area(
                    "Custom telehealth keywords (one per line):",
                    value="\n".join(self.telehealth_keywords[:10]),  # Show first 10 as examples
                    height=100,
                    help="Add custom telehealth-related keywords to search for"
                )
                
                # Update telehealth keywords if custom ones provided
                if custom_telehealth.strip():
                    custom_keywords = [keyword.strip() for keyword in custom_telehealth.split('\n') if keyword.strip()]
                    if custom_keywords:
                        self.telehealth_keywords = custom_keywords
        
        # State selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Select States for Licensing:**")
            selected_states = st.multiselect(
                "States (select multiple):",
                options=list(self.state_abbreviations.keys()),
                default=['california', 'texas'],
                help="Select states where you need the nurse practitioner to be licensed"
            )
        
        with col2:
            st.write("**Search Criteria:**")
            # Removed: Minimum states licensed in control
            
            require_telehealth = st.checkbox(
                "Require telehealth experience",
                value=True,
                help="Only show candidates with telehealth/remote care experience"
            )
            
            # Creative search options
            search_strategy = st.selectbox(
                "Search Strategy:",
                ["Comprehensive (all fields)", "Job-focused (title + description)", "Skills-focused (skills + education)", "LinkedIn-focused (headline + description)"],
                help="Choose how aggressively to search for nurse practitioners and telehealth experience"
            )
        
        # Show search preview
        with st.expander("🔍 Search Strategy Preview"):
            st.write("**Nurse Titles Being Searched:**")
            st.code(", ".join(self.nurse_titles[:15]) + ("..." if len(self.nurse_titles) > 15 else ""))
            
            st.write("**Telehealth Keywords Being Searched:**")
            st.code(", ".join(self.telehealth_keywords[:15]) + ("..." if len(self.telehealth_keywords) > 15 else ""))
            
            st.write("**Fields Being Checked:**")
            fields_to_check = ["JOB_TITLE", "JOB_FUNCTION", "JOB_DESCRIPTION", "LINKEDIN_HEADLINE", "SKILLS", "EDUCATION"]
            st.code(", ".join(fields_to_check))
        
        # Search button
        if st.button("🔍 Search Nurse Practitioners", type="primary"):
            if not selected_states:
                st.warning("Please select at least one state")
                return None
            
            with st.spinner("Searching for nurse practitioners..."):
                # Default min_states to 1 internally (no user control)
                results = self.search_nurse_practitioners(
                    states=selected_states,
                    min_states=1,
                    require_telehealth=require_telehealth
                )
                
                if results is not None and not results.empty:
                    st.success(f"Found {len(results)} nurse practitioner candidates!")
                    return results
                else:
                    st.info("No results found. Try adjusting your search criteria or adding more keywords.")
                    return None
        
        return None
    
    def analyze_results(self, results_df):
        """Analyze and display search results with insights"""
        
        if results_df is None or results_df.empty:
            return
        
        # Debug: Show what columns we actually have
        st.write("**Debug - Available columns:**")
        st.write(list(results_df.columns))
        
        # Debug: Show first few rows to understand the data structure
        st.write("**Debug - First few rows:**")
        st.write(results_df.head(3))
        
        st.subheader("📊 Search Results Analysis")
        
        # Key metrics with robust error handling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", len(results_df))
        
        with col2:
            # Check if the column exists and use the correct name
            try:
                if 'STATES_LICENSED_IN' in results_df.columns:
                    avg_states = results_df['STATES_LICENSED_IN'].mean()
                    st.metric("Avg States Licensed", f"{avg_states:.1f}")
                elif 'states_licensed_in' in results_df.columns:
                    avg_states = results_df['states_licensed_in'].mean()
                    st.metric("Avg States Licensed", f"{avg_states:.1f}")
                else:
                    st.metric("Avg States Licensed", "N/A")
            except Exception as e:
                st.metric("Avg States Licensed", f"Error: {str(e)}")
        
        with col3:
            # Check if the column exists and use the correct name
            try:
                if 'HAS_TELEHEALTH_EXPERIENCE' in results_df.columns:
                    telehealth_count = results_df['HAS_TELEHEALTH_EXPERIENCE'].sum()
                    st.metric("With Telehealth Exp", telehealth_count)
                elif 'has_telehealth_experience' in results_df.columns:
                    telehealth_count = results_df['has_telehealth_experience'].sum()
                    st.metric("With Telehealth Exp", telehealth_count)
                else:
                    st.metric("With Telehealth Exp", "N/A")
            except Exception as e:
                st.metric("With Telehealth Exp", f"Error: {str(e)}")
        
        with col4:
            try:
                unique_companies = results_df['COMPANY_NAME'].nunique()
                st.metric("Unique Companies", unique_companies)
            except Exception as e:
                st.metric("Unique Companies", f"Error: {str(e)}")
        
        # Results table
        st.subheader("Candidate Details")
        st.dataframe(results_df, use_container_width=True)
        
        # Download options
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            try:
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="nurse_practitioner_candidates.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"CSV download error: {str(e)}")
        
        with col_dl2:
            # Create a summary report
            try:
                summary = self._create_summary_report(results_df)
                st.download_button(
                    label="📄 Download Summary Report",
                    data=summary,
                    file_name="np_search_summary.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Summary report error: {str(e)}")
                st.write("**Error creating summary report:**")
                st.write(str(e))
        
        # Detailed analysis tabs
        tab1, tab2, tab3 = st.tabs(["State Distribution", "Company Analysis", "Skills Analysis"])
        
        with tab1:
            try:
                self._show_state_distribution(results_df)
            except Exception as e:
                st.error(f"State distribution error: {str(e)}")
        
        with tab2:
            try:
                self._show_company_analysis(results_df)
            except Exception as e:
                st.error(f"Company analysis error: {str(e)}")
        
        with tab3:
            try:
                self._show_skills_analysis(results_df)
            except Exception as e:
                st.error(f"Skills analysis error: {str(e)}")
    
    def _create_summary_report(self, results_df):
        """Create a text summary report of the search results"""
        
        # Get the correct column names
        states_col = 'STATES_LICENSED_IN' if 'STATES_LICENSED_IN' in results_df.columns else 'states_licensed_in'
        telehealth_col = 'HAS_TELEHEALTH_EXPERIENCE' if 'HAS_TELEHEALTH_EXPERIENCE' in results_df.columns else 'has_telehealth_experience'
        
        # Safely get values with fallbacks
        try:
            avg_states = results_df[states_col].mean() if states_col in results_df.columns else 0
        except:
            avg_states = 0
            
        try:
            telehealth_count = results_df[telehealth_col].sum() if telehealth_col in results_df.columns else 0
        except:
            telehealth_count = 0
            
        try:
            top_candidates = results_df.nlargest(5, states_col)[['FIRST_NAME', 'LAST_NAME', states_col, 'COMPANY_NAME']].to_string(index=False) if states_col in results_df.columns else "Data not available"
        except:
            top_candidates = "Data not available"
        
        report = f"""
NURSE PRACTITIONER SEARCH SUMMARY REPORT
========================================

Search Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Candidates Found: {len(results_df)}

KEY STATISTICS:
- Average states licensed in: {avg_states:.1f}
- Candidates with telehealth experience: {telehealth_count}
- Unique companies represented: {results_df['COMPANY_NAME'].nunique()}

TOP CANDIDATES (by states licensed):
{top_candidates}

COMPANIES WITH MOST CANDIDATES:
{results_df['COMPANY_NAME'].value_counts().head(10).to_string()}

STATE DISTRIBUTION:
{results_df['JOB_LOCATION_STATE_CODE'].value_counts().head(10).to_string()}

This report was generated automatically by the Nurse Practitioner Search Tool.
        """
        
        return report
    
    def _show_state_distribution(self, results_df):
        """Show distribution of candidates across states"""
        
        state_counts = results_df['JOB_LOCATION_STATE_CODE'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Candidates per State:**")
            st.dataframe(state_counts.reset_index().rename(
                columns={'index': 'State', 'JOB_LOCATION_STATE_CODE': 'Count'}
            ))
        
        with col2:
            st.write("**States vs Candidates:**")
            # Simple bar chart using streamlit
            st.bar_chart(state_counts.head(10))
    
    def _show_company_analysis(self, results_df):
        """Show analysis of companies"""
        
        company_counts = results_df['COMPANY_NAME'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top Companies:**")
            st.dataframe(company_counts.head(10).reset_index().rename(
                columns={'index': 'Company', 'COMPANY_NAME': 'Candidate Count'}
            ))
        
        with col2:
            st.write("**Company Distribution:**")
            st.bar_chart(company_counts.head(10))
    
    def _show_skills_analysis(self, results_df):
        """Show analysis of skills and education"""
        
        # Skills analysis
        if 'SKILLS' in results_df.columns:
            st.write("**Skills Analysis:**")
            skills_text = ' '.join(results_df['SKILLS'].dropna().astype(str))
            if skills_text:
                # Simple word frequency (basic approach)
                words = skills_text.lower().split()
                word_freq = pd.Series(words).value_counts().head(20)
                st.bar_chart(word_freq)
        
        # Education analysis
        if 'EDUCATION' in results_df.columns:
            st.write("**Education Analysis:**")
            education_counts = results_df['EDUCATION'].value_counts().head(10)
            st.dataframe(education_counts.reset_index().rename(
                columns={'index': 'Education', 'EDUCATION': 'Count'}
            ))


def main():
    """Main function for testing the nurse practitioner search"""
    
    st.title("🏥 Nurse Practitioner Search Tool")
    
    # Initialize the search class
    np_search = NursePractitionerSearch()
    
    # Show the advanced search UI
    results = np_search.get_advanced_search_ui()
    
    # If we have results, analyze them
    if results is not None:
        np_search.analyze_results(results)


if __name__ == "__main__":
    main() 