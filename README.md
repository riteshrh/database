# ❄️🏥 Snowflake Natural Language Query & Nurse Practitioner Search

A powerful Streamlit application that combines natural language to SQL conversion with specialized healthcare professional search capabilities. Perfect for HR teams, recruiters, and healthcare organizations looking to find qualified candidates.

## 🚀 Features

### 🔍 General Natural Language Query Interface
- **Natural Language to SQL**: Convert plain English queries to Snowflake SQL using OpenAI GPT-4
- **Smart Query Generation**: AI-powered SQL generation with database schema awareness
- **Query Validation**: Built-in safety checks to prevent dangerous operations
- **Results Analysis**: Comprehensive data analysis with download options

### 🏥 Specialized Nurse Practitioner Search
- **Multi-State Licensing**: Find NPs licensed in multiple states simultaneously
- **Telehealth Experience**: Identify candidates with remote care experience
- **Advanced Filtering**: Refine searches by location, company, and skills
- **Comprehensive Analysis**: Detailed insights and reporting capabilities

## 🏗️ Architecture

The application consists of three main components:

1. **`main_app.py`** - Main application with dual interface
2. **`nurse_practitioner_search.py`** - Specialized NP search functionality
3. **`app.py`** - Original general query interface (standalone)

## 📋 Prerequisites

- Python 3.8+
- Snowflake account with access to the specified tables
- OpenAI API key
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd snowflake_natural_language_query
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root with the following variables:
   ```env
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Snowflake Database Configuration
   SNOWFLAKE_USER=your_snowflake_username
   SNOWFLAKE_PASSWORD=your_snowflake_password
   SNOWFLAKE_ACCOUNT=your_snowflake_account_identifier
   SNOWFLAKE_WAREHOUSE=your_warehouse_name
   SNOWFLAKE_DATABASE=userprofiles
   SNOWFLAKE_SCHEMA=public
   ```

## 🚀 Usage

### Running the Application

1. **Main Application (Recommended):**
   ```bash
   streamlit run main_app.py
   ```

2. **Standalone General Query Interface:**
   ```bash
   streamlit run app.py
   ```

3. **Nurse Practitioner Search Only:**
   ```bash
   streamlit run nurse_practitioner_search.py
   ```

### Using the General Query Interface

1. **Select "General Query"** from the sidebar
2. **Enter your natural language query**, for example:
   - "Find nurse practitioners licensed in California and Texas with telehealth experience"
   - "Show all software engineers with Python skills in San Francisco"
   - "Find companies in the healthcare industry with more than 1000 employees"
3. **Click "Convert to SQL"** to generate the SQL query
4. **Review the generated SQL** and click "Execute Query" to run it
5. **Analyze results** with built-in data analysis tools
6. **Download results** in CSV or Excel format

### Using the Nurse Practitioner Search

1. **Select "Nurse Practitioner Search"** from the sidebar
2. **Choose target states** for licensing requirements
3. **Set minimum states** the candidate should be licensed in
4. **Toggle telehealth requirement** if needed
5. **Click "Search Nurse Practitioners"** to execute the search
6. **Review comprehensive results** with detailed analysis
7. **Download candidate lists** and summary reports

## 🗄️ Database Schema

The application works with three main Snowflake tables:

### `userprofiles.public.contact_search_dz`
- Contact information and job details
- Skills, education, and certifications
- Job location and company information
- LinkedIn profile data

### `userprofiles.public.org_latest_copy`
- Organization and company information
- Industry classifications and employee counts
- Geographic and contact information

### `userprofiles.public.per_latest_copy`
- Detailed person profiles
- Advanced skills and certifications
- Professional experience and education

## 🔍 Search Capabilities

### Nurse Practitioner Search Features

- **Job Title Matching**: Identifies various nurse practitioner roles
- **State Licensing**: Multi-state licensing verification
- **Telehealth Experience**: Keyword-based telehealth experience detection
- **Skills Analysis**: Education and certification analysis
- **Company Insights**: Employer and industry analysis

### General Query Capabilities

- **Natural Language Processing**: Human-readable query input
- **AI-Powered SQL Generation**: Intelligent query construction
- **Schema Awareness**: Database-aware query optimization
- **Safety Validation**: Query security and validation

## 📊 Output and Analysis

### Results Display
- **Interactive DataFrames**: Sortable and filterable results
- **Key Metrics**: Row counts, column information, memory usage
- **Data Preview**: First 10 rows, data types, missing values analysis

### Download Options
- **CSV Export**: Standard comma-separated values
- **Excel Export**: Multi-sheet Excel files with formatting
- **Summary Reports**: Text-based analysis summaries

### Analysis Features
- **State Distribution**: Geographic analysis of candidates
- **Company Analysis**: Employer distribution and insights
- **Skills Analysis**: Skills and education breakdown

## 🛡️ Security Features

- **SQL Injection Prevention**: Parameterized queries and validation
- **Dangerous Operation Blocking**: Prevents DROP, DELETE, ALTER operations
- **Read-Only Enforcement**: SELECT-only query execution
- **Connection Management**: Secure database connection handling

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `SNOWFLAKE_USER` | Snowflake username | Yes |
| `SNOWFLAKE_PASSWORD` | Snowflake password | Yes |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier | Yes |
| `SNOWFLAKE_WAREHOUSE` | Snowflake warehouse name | Yes |
| `SNOWFLAKE_DATABASE` | Database name (default: userprofiles) | Yes |
| `SNOWFLAKE_SCHEMA` | Schema name (default: public) | Yes |

### Customization

The application can be customized by modifying:

- **Search Keywords**: Update nurse titles and telehealth keywords in `nurse_practitioner_search.py`
- **Database Schema**: Modify the schema information in the main application files
- **UI Elements**: Customize Streamlit components and styling
- **Query Logic**: Adjust the SQL generation prompts and logic

## 🚨 Troubleshooting

### Common Issues

1. **Connection Errors**: Verify Snowflake credentials and network access
2. **OpenAI API Errors**: Check API key validity and quota limits
3. **Query Generation Failures**: Ensure natural language queries are clear and specific
4. **No Results**: Verify search criteria and database content

### Debug Mode

Enable debug logging by setting environment variables:
```env
LOG_LEVEL=DEBUG
```

## 📈 Performance Optimization

- **Query Optimization**: Use specific search criteria to reduce result sets
- **Connection Pooling**: Efficient database connection management
- **Caching**: Session state management for repeated queries
- **Batch Processing**: Handle large result sets efficiently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section
2. Review the configuration requirements
3. Verify database connectivity
4. Check OpenAI API status

## 🔮 Future Enhancements

- **Additional Healthcare Roles**: Expand beyond nurse practitioners
- **Advanced Analytics**: Machine learning-based candidate scoring
- **Integration APIs**: Connect with ATS and HR systems
- **Mobile Support**: Responsive design for mobile devices
- **Multi-language Support**: Internationalization capabilities

---

**Built with ❤️ for healthcare recruitment and data analysis** 