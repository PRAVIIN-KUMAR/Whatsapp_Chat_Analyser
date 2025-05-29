import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

# Page config for better look
st.set_page_config(page_title="📊 WhatsApp Chat Analyzer", layout="wide",initial_sidebar_state="expanded"
)

# Sidebar Styling & Content
st.sidebar.title("💬 WhatsApp Chat Analyzer")
st.sidebar.markdown(
    """
    <div style="font-size:16px; line-height:1.6;">
    Analyze your WhatsApp chats like a pro!  
    Upload your exported chat file and explore:
    <ul>
        <li>📈 Detailed message stats</li>
        <li>📅 Monthly & daily timelines</li>
        <li>🔥 Activity heatmaps</li>
        <li>🗣️ Most active users & word clouds</li>
        <li>😊 Emoji usage insights</li>
    </ul>
    <b>How to use:</b><br>
    1️⃣ Export your WhatsApp chat without media.<br>
    2️⃣ Upload the chat (.txt) file here.<br>
    3️⃣ Select a user or Overall.<br>
    4️⃣ Click <b>Show Analysis</b> and explore!<br><br>
    <i style="color:#666;">Made with ❤️ using Python & Streamlit</i>
    </div>
    """, unsafe_allow_html=True
)

# File uploader with info
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat File (.txt)", type=["txt"])

if uploaded_file is not None:
    # Decode uploaded file
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    with st.spinner("Processing chat... ⏳"):
        df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Select User for Analysis", user_list)

    if st.sidebar.button("Show Analysis"):
        st.markdown(f"## 📊 Analysis for: **{selected_user}**")

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4, gap="large")

        with col1:
            st.metric(label="💬 Total Messages", value=num_messages)
        with col2:
            st.metric(label="📝 Total Words", value=words)
        with col3:
            st.metric(label="📷 Media Shared", value=num_media_messages)
        with col4:
            st.metric(label="🔗 Links Shared", value=num_links)

        # Monthly Timeline
        st.markdown("### 📅 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timeline['time'], timeline['message'], marker='o', color='#1f77b4')
        ax.set_xlabel('Month-Year')
        ax.set_ylabel('Messages')
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Daily Timeline
        st.markdown("### 📆 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#ff7f0e')
        ax.set_xlabel('Date')
        ax.set_ylabel('Messages')
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        fig.tight_layout()
        st.pyplot(fig)

        # Activity Map
        st.markdown("### 🔥 Activity Map")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("**Most Busy Day of Week**")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_day.index, y=busy_day.values, palette="viridis", ax=ax)
            ax.set_ylabel('Messages')
            st.pyplot(fig)
        with col2:
            st.markdown("**Most Busy Month**")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_month.index, y=busy_month.values, palette="magma", ax=ax)
            ax.set_ylabel('Messages')
            st.pyplot(fig)

        # Weekly Heatmap
        st.markdown("### 📊 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.heatmap(user_heatmap, cmap="YlGnBu", linecolor='white', linewidth=0.5, ax=ax)
        st.pyplot(fig)

        # Most Busy Users (Overall only)
        if selected_user == 'Overall':
            st.markdown("### 🏅 Most Busy Users")
            busy_users, user_df = helper.most_busy_users(df)
            col1, col2 = st.columns([3, 2], gap="large")
            with col1:
                fig, ax = plt.subplots(figsize=(8,4))
                sns.barplot(x=busy_users.values, y=busy_users.index, palette='rocket', ax=ax)
                ax.set_xlabel("Messages")
                ax.set_ylabel("Users")
                st.pyplot(fig)
            with col2:
                st.dataframe(user_df)

        # Word Cloud
        st.markdown("### ☁️ Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        # Most Common Words
        most_common_df = helper.most_common_words(selected_user, df)
        st.markdown("### 🔤 Most Common Words")
        fig, ax = plt.subplots(figsize=(8,5))
        ax.barh(most_common_df[0], most_common_df[1], color='#e74c3c')
        ax.invert_yaxis()
        st.pyplot(fig)

        # Emoji Analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.markdown("### 😍 Emoji Analysis")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1], labels=emoji_df[0], autopct='%1.1f%%', startangle=140, textprops={'fontsize': 12})
            ax.axis('equal')
            st.pyplot(fig)

else:
    st.sidebar.info("👉 Upload your WhatsApp chat `.txt` file to start analysis.")
    st.markdown(
        """
        <div style="text-align:center; margin-top: 4rem;">
            <h2 style="color:#4a90e2;">Welcome to WhatsApp Chat Analyzer! 💬</h2>
            <p style="font-size:18px; color:#555;">
            Please upload your exported WhatsApp chat file from the sidebar to get started.<br><br>
            <span style="font-size:40px;">📂⬆️</span>
            </p>
        </div>
        """, unsafe_allow_html=True
    )
