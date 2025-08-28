import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="מנתח משמרות שומרים",
    page_icon="👮‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('shifts_structured_long.csv')
    # Clean column names by stripping whitespace
    df.columns = df.columns.str.strip()
    # Remove duplicates based on all columns
    df = df.drop_duplicates()
    # Convert hour column to time format for better sorting
    df['hour_sort'] = pd.to_datetime(df['hour'], format='%H:%M').dt.time
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    return df

def main():
    st.title("🔍 מנתח משמרות שומרים")
    st.markdown("---")
    
    # Load data
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("❌ קובץ CSV 'shifts_structured_long.csv' לא נמצא. אנא ודא שהקובץ נמצא באותה תיקייה כמו הסקריפט.")
        return
    
    # Show data info
    total_records_before = pd.read_csv('shifts_structured_long.csv').shape[0]
    total_records_after = df.shape[0]
    duplicates_removed = total_records_before - total_records_after
    
    if duplicates_removed > 0:
        st.info(f"ℹ️ הוסרו {duplicates_removed} רשומות כפולות. עובדים עם {total_records_after} משמרות ייחודיות.")
    
    # Create main navigation
    page = st.sidebar.radio(
        "ניווט",
        ["🏆 שומרים מובילים", "👤 ניתוח שומר יחיד"]
    )
    
    if page == "🏆 שומרים מובילים":
        show_top_guards_page(df)
    else:
        show_individual_guard_page(df)
def show_top_guards_page(df):
    """Display the top guards dashboard"""
    st.header("🏆 לוח שומרים מובילים")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_guards = df['guard_name'].nunique()
        st.metric("סה״כ שומרים", total_guards)
    
    with col2:
        total_shifts = len(df)
        st.metric("סה״כ משמרות", total_shifts)
    
    with col3:
        unique_positions = df['position'].nunique()
        st.metric("עמדות ייחודיות", unique_positions)
    
    with col4:
        unique_hours = df['hour'].nunique()
        st.metric("שעות שונות", unique_hours)
    
    st.markdown("---")
    
    # Create tabs for different top guard views
    tab1, tab2, tab3 = st.tabs(["📊 שומרים הכי פעילים", "⏰ מובילים לפי שעה", "🏢 מובילים לפי עמדה"])
    
    with tab1:
        st.subheader("שומרים הכי פעילים (סה״כ משמרות)")
        
        # Calculate total shifts per guard
        guard_shifts = df.groupby('guard_name').size().reset_index()
        guard_shifts.columns = ['שם השומר', 'סה״כ משמרות']
        guard_shifts = guard_shifts.sort_values('סה״כ משמרות', ascending=False)
        
        # Top 10 guards chart
        top_guards = guard_shifts.head(10)
        
        fig_top_guards = px.bar(
            top_guards,
            x='סה״כ משמרות',
            y='שם השומר',
            orientation='h',
            title="10 השומרים הכי פעילים",
            color='סה״כ משמרות',
            color_continuous_scale='viridis'
        )
        fig_top_guards.update_layout(height=500)
        st.plotly_chart(fig_top_guards, use_container_width=True)
        
        # Full rankings table
        st.subheader("דירוג מלא")
        guard_shifts['דירוג'] = range(1, len(guard_shifts) + 1)
        guard_shifts = guard_shifts[['דירוג', 'שם השומר', 'סה״כ משמרות']]
        st.dataframe(guard_shifts, use_container_width=True, height=400)
    
    with tab2:
        st.subheader("שומרים מובילים לפי שעה")
        
        # Create hour selector
        available_hours = sorted(df['hour'].unique())
        selected_hour = st.selectbox("בחר שעה:", available_hours)
        
        # Filter data for selected hour
        hour_data = df[df['hour'] == selected_hour]
        hour_guard_counts = hour_data.groupby('guard_name').size().reset_index()
        hour_guard_counts.columns = ['שם השומר', 'משמרות']
        hour_guard_counts = hour_guard_counts.sort_values('משמרות', ascending=False)
        
        # Top guards for this hour
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_hour_guards = hour_guard_counts.head(10)
            fig_hour = px.bar(
                top_hour_guards,
                x='שם השומר',
                y='משמרות',
                title=f"שומרים מובילים עבור {selected_hour}",
                color='משמרות',
                color_continuous_scale='plasma'
            )
            fig_hour.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_hour, use_container_width=True)
        
        with col2:
            st.write(f"**5 הראשונים עבור {selected_hour}:**")
            for i, row in hour_guard_counts.head(5).iterrows():
                st.write(f"{row['שם השומר']}: {row['משמרות']} משמרות")
        
        # Hour performance heatmap for all guards
        st.subheader("ביצועי שומרים לפי שעה (מפת חום)")
        hour_matrix = df.groupby(['guard_name', 'hour']).size().unstack(fill_value=0)
        
        # Show only top 15 most active guards for readability
        top_15_guards = df.groupby('guard_name').size().nlargest(15).index
        hour_matrix_filtered = hour_matrix.loc[top_15_guards]
        
        fig_heatmap = px.imshow(
            hour_matrix_filtered,
            title="15 השומרים המובילים - משמרות לפי שעה",
            labels=dict(x="שעה", y="שומר", color="משמרות"),
            color_continuous_scale='Blues',
            aspect="auto"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab3:
        st.subheader("שומרים מובילים לפי עמדה")
        
        # Create position selector
        available_positions = sorted(df['position'].unique())
        selected_position = st.selectbox("בחר עמדה:", available_positions)
        
        # Filter data for selected position
        position_data = df[df['position'] == selected_position]
        position_guard_counts = position_data.groupby('guard_name').size().reset_index()
        position_guard_counts.columns = ['שם השומר', 'משמרות']
        position_guard_counts = position_guard_counts.sort_values('משמרות', ascending=False)
        
        # Top guards for this position
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_position_guards = position_guard_counts.head(10)
            fig_position = px.bar(
                top_position_guards,
                x='שם השומר',
                y='משמרות',
                title=f"שומרים מובילים עבור {selected_position}",
                color='משמרות',
                color_continuous_scale='viridis'
            )
            fig_position.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_position, use_container_width=True)
        
        with col2:
            st.write(f"**5 הראשונים עבור {selected_position}:**")
            for i, row in position_guard_counts.head(5).iterrows():
                st.write(f"{row['שם השומר']}: {row['משמרות']} משמרות")
        
        # Position distribution for all guards
        st.subheader("התפלגות שומרים בכל העמדות")
        position_matrix = df.groupby(['guard_name', 'position']).size().unstack(fill_value=0)
        
        # Show only top 15 most active guards
        position_matrix_filtered = position_matrix.loc[top_15_guards]
        
        fig_pos_heatmap = px.imshow(
            position_matrix_filtered,
            title="15 השומרים המובילים - משמרות לפי עמדה",
            labels=dict(x="עמדה", y="שומר", color="משמרות"),
            color_continuous_scale='Viridis',
            aspect="auto"
        )
        st.plotly_chart(fig_pos_heatmap, use_container_width=True)


def show_individual_guard_page(df):
    """Display individual guard analysis"""
    st.header("👤 ניתוח שומר יחיד")
    
    # Sidebar for guard selection
    st.sidebar.header("בחר שומר")
    
    # Get unique guard names
    guard_names = sorted(df['guard_name'].unique())
    
    selected_guard = st.sidebar.selectbox(
        "בחר שומר:",
        guard_names,
        index=0
    )
    
    # Filter data for selected guard
    guard_data = df[df['guard_name'] == selected_guard].copy()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 סטטיסטיקות משמרות עבור {selected_guard}")
    
    with col2:
        # Display total shifts
        total_shifts = len(guard_data)
        st.metric("סה״כ משמרות", total_shifts)
    
    if len(guard_data) == 0:
        st.warning("לא נמצאו נתוני משמרות עבור השומר הנבחר.")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📈 ניתוח עמדות", "⏰ התפלגות שעתית"])
    
    with tab1:
        st.subheader("הרכב עמדות")
        
        # Position statistics
        position_counts = guard_data['position'].value_counts()
        position_percentages = (position_counts / total_shifts * 100).round(1)
        
        # Create two columns for position analysis
        pos_col1, pos_col2 = st.columns([1, 1])
        
        with pos_col1:
            # Position pie chart
            fig_pie = px.pie(
                values=position_counts.values,
                names=position_counts.index,
                title="התפלגות עמדות",
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with pos_col2:
            # Position bar chart
            fig_bar = px.bar(
                x=position_counts.index,
                y=position_counts.values,
                title="משמרות לפי עמדה",
                labels={'x': 'עמדה', 'y': 'מספר משמרות'},
                color=position_counts.values,
                color_continuous_scale='viridis'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Position statistics table
        st.subheader("טבלת סטטיסטיקות עמדות")
        position_stats = pd.DataFrame({
            'עמדה': position_counts.index,
            'מספר משמרות': position_counts.values,
            'אחוז': [f"{pct}%" for pct in position_percentages.values]
        })
        st.dataframe(position_stats, use_container_width=True)
    
    with tab2:
        st.subheader("התפלגות שעתית")
        
        # Hourly statistics
        hourly_counts = guard_data['hour'].value_counts().sort_index()
        
        # Create two columns for hourly analysis
        hour_col1, hour_col2 = st.columns([2, 1])
        
        with hour_col1:
            # Hourly bar chart
            fig_hourly = px.bar(
                x=hourly_counts.index,
                y=hourly_counts.values,
                title="משמרות לפי שעה",
                labels={'x': 'שעה', 'y': 'מספר משמרות'},
                color=hourly_counts.values,
                color_continuous_scale='plasma'
            )
            fig_hourly.update_layout(showlegend=False)
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with hour_col2:
            # Hourly statistics table
            st.subheader("סטטיסטיקות שעות")
            hourly_stats = pd.DataFrame({
                'שעה': hourly_counts.index,
                'משמרות': hourly_counts.values,
                'אחוז': [(count/total_shifts*100) for count in hourly_counts.values]
            })
            hourly_stats['אחוז'] = hourly_stats['אחוז'].round(1).astype(str) + '%'
            st.dataframe(hourly_stats, use_container_width=True)
        
        # Combined hour and position heatmap
        st.subheader("מפת חום שעה מול עמדה")
        heatmap_data = guard_data.groupby(['hour', 'position']).size().unstack(fill_value=0)
        
        if not heatmap_data.empty:
            fig_heatmap = px.imshow(
                heatmap_data.T,
                title="התפלגות משמרות: שעה מול עמדה",
                labels=dict(x="שעה", y="עמדה", color="מספר משמרות"),
                aspect="auto",
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Additional information section
    st.markdown("---")
    st.subheader("📋 משמרות אחרונות")
    
    # Show last 10 shifts
    recent_shifts = guard_data.sort_values(['date', 'hour'], ascending=[False, False]).head(10)
    recent_shifts_display = recent_shifts[['date', 'hour', 'position']].copy()
    recent_shifts_display['date'] = recent_shifts_display['date'].dt.strftime('%d/%m/%Y')
    recent_shifts_display.columns = ['תאריך', 'שעה', 'עמדה']
    
    st.dataframe(recent_shifts_display, use_container_width=True)
    
    # Summary statistics
    st.markdown("---")
    st.subheader("📈 סטטיסטיקות סיכום")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        unique_positions = guard_data['position'].nunique()
        st.metric("עמדות ייחודיות", unique_positions)
    
    with summary_col2:
        unique_hours = guard_data['hour'].nunique()
        st.metric("שעות שונות", unique_hours)
    
    with summary_col3:
        most_common_position = guard_data['position'].mode().iloc[0] if len(guard_data) > 0 else "לא זמין"
        st.metric("עמדה הכי נפוצה", most_common_position)
    
    with summary_col4:
        most_common_hour = guard_data['hour'].mode().iloc[0] if len(guard_data) > 0 else "לא זמין"
        st.metric("שעה הכי נפוצה", most_common_hour)

if __name__ == "__main__":
    main()
