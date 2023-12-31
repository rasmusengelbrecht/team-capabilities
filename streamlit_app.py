import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

# Set page layout
st.set_page_config(page_title="Team Capabilities", page_icon=":spider_web:",layout="wide")

# Title and description
st.title("Team Capabilities Visualization")

##################### Data Input Section #####################
st.header("Data Input")
input_col1, input_col2 = st.columns(2)

# Team members
team_member_input = input_col1.text_input("Enter the names of team members (comma-separated)", "John, Jane, Alice, Bob")
team_member_list = [member.strip() for member in team_member_input.split(",")]

# Capabilities
capability_input = input_col2.text_input("Enter the capabilities (comma-separated)", "Capability 1, Capability 2, Capability 3")
capability_list = [capability.strip() for capability in capability_input.split(",")]

# Team type selection
show_team_type = input_col2.checkbox("Try a team template instead")
if show_team_type:
    team_type = st.selectbox("Select Team Type", ("", "Data", "UX", "Design", "Product", "Engineering"))
    if team_type:
        template_capabilities = {
            "Data": "Statistics, Visualization, SQL, Programming, Spreadsheets, Storytelling",
            "UX": "User Research, Wireframing, Prototyping, Usability Testing, Interaction Design",
            "Design": "Graphic Design, Typography, Color Theory, Layout, Branding",
            "Product": "Product Strategy, Market Research, Agile Methodology, User Feedback, Roadmapping",
            "Engineering": "Software Development, Algorithms, Data Structures, Testing, Debugging"
        }
        capability_input = template_capabilities.get(team_type, "")
        capability_list = [capability.strip() for capability in capability_input.split(",")]


##################### CSV Upload and Export #####################
with st.expander("Saved data from earlier? Upload your CSV here!"):

    # CSV upload
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv", "txt"])

    if uploaded_file is not None:
        # Read the uploaded file
        if uploaded_file.name.lower().endswith('.csv'):
            delimiter = ','
        else:
            delimiter = ';'
        csv_data = pd.read_csv(uploaded_file, delimiter=delimiter)

        # Extract team members and capability ratings
        team_member_list = csv_data.columns[1:].tolist()
        capability_list = csv_data.iloc[:, 0].tolist()
        capability_ratings = csv_data.iloc[:, 1:].values.tolist()

        # Create DataFrame for stacked radar chart of the entire team
        team_df = pd.DataFrame(capability_ratings, columns=team_member_list, index=capability_list)

    else:
        # Create DataFrame for stacked radar chart of the entire team
        team_df = pd.DataFrame(index=capability_list)
        for member in team_member_list:
            team_df[member] = [5] * len(capability_list)

# Add space
st.markdown("---")

##################### Team Member Section #####################
st.header("Team Members \U0001F9B8")

# Display team members in two columns
num_columns = 2
num_members = len(team_member_list)
num_rows = (num_members + num_columns - 1) // num_columns

# Create layout for team members in two columns
col1, col2 = st.columns(2)

# Define color palette
color_palette = [
    "#0074D9", "#4287F5", "#748DF6", "#A393F7", "#D49AF8",
    "#FFA500", "#FF8800", "#FF6600", "#FF4400", "#FF2200"
]

# Iterate over team members and display their capabilities
for i, member in enumerate(team_member_list):
    # Capability ratings
    ratings_data = team_df[member].values.tolist()
    with col1 if i % num_columns == 0 else col2:
        st.header(member)

        # Create columns for radar chart and ratings
        chart_col, rating_col = st.columns(2)

        for j, capability in enumerate(capability_list):
            key = f"{member}_{j}_rating"  # Unique key for each slider
            rating = rating_col.slider(f"{capability}", 1, 10, ratings_data[j], key=key)
            ratings_data[j] = rating

        # Update DataFrame with capability ratings
        team_df[member] = ratings_data

        # Create DataFrame for radar chart
        df = pd.DataFrame({member: ratings_data}, index=capability_list)

        # Generate radar chart for the team member
        fig = go.Figure(data=go.Scatterpolar(
            r=df[member],
            theta=df.index,
            fill='toself',
            name=member,
            mode='lines',
            marker=dict(color=color_palette[i % len(color_palette)])
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 10]
                )
            ),
            showlegend=False
        )

        # Display radar chart for the team member
        chart_col.plotly_chart(fig, use_container_width=True)

# Add space
st.markdown("---")

##################### Team Section #####################
st.header("Team Capabilities \U0001F9D1")

# Generate stacked radar chart for the entire team
team_fig = go.Figure()
for i, member in enumerate(team_member_list):
    team_fig.add_trace(go.Scatterpolar(
        r=team_df[member],
        theta=team_df.index,
        fill='toself',
        name=member,
        mode='lines',
        marker=dict(color=color_palette[i % len(color_palette)]),
        opacity=0.4
    ))
team_fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=False,
            range=[0, 10],
        )
    ),
    showlegend=True,
    legend=dict(
        orientation="h",
        xanchor="center",
        x=0.5,
        y=-0.3
    ),
    height=700  # Adjust the height of the plot
)

# Calculate average capability ratings
average_ratings = team_df.mean(axis=1)

# Find capability to improve and team's best capability
lowest_capability = average_ratings.idxmin()
highest_capability = average_ratings.idxmax()

# Generate text output if highest_capability and lowest_capability are not equal
if highest_capability != lowest_capability:
    best_text = f"The team's best capability is **{highest_capability}** \U0001F44D"
    improve_text = f"The team needs to improve in **{lowest_capability}** \U0001F4DA"
    st.markdown(best_text)
    st.markdown(improve_text)

# Display stacked radar chart for the entire team
st.plotly_chart(team_fig, use_container_width=True)

##################### CSV Export #####################
csv_export = team_df.reset_index().to_csv(index=False)  # Convert DataFrame to CSV format
b64 = base64.b64encode(csv_export.encode()).decode()  # Encode CSV as base64
href = f'<a href="data:file/csv;base64,{b64}" download="team_capabilities.csv">Download CSV</a>'  # Create download link
st.markdown("---")
st.markdown("### CSV Export")
st.markdown("Click the link below to download the team capabilities CSV file:")
st.markdown(href, unsafe_allow_html=True)  # Display download link
