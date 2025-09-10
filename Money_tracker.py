import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os

# Page configuration
st.set_page_config(
    page_title="💸 Friend Money Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .person-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .person-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .owe-me {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 15px;
        border-radius: 12px;
        color: #1a1a1a;
        font-weight: bold;
    }
    .i-owe {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
    }
    .neutral {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 15px;
        border-radius: 12px;
        color: #1a1a1a;
        font-weight: bold;
    }
    .transaction-item {
        background: white;
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        border-left: 4px solid;
        transition: all 0.2s;
    }
    .transaction-item:hover {
        transform: translateX(5px);
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    .given-transaction {
        border-left-color: #48bb78;
    }
    .taken-transaction {
        border-left-color: #f56565;
    }
    .settled-transaction {
        border-left-color: #a0aec0;
        opacity: 0.7;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'show_person_details' not in st.session_state:
    st.session_state.show_person_details = {}

# Data file path
DATA_FILE = "money_tracker_data.json"

# Load data from file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                st.session_state.transactions = data.get('transactions', [])
        except:
            pass

# Save data to file
def save_data():
    data = {
        'transactions': st.session_state.transactions
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Load data on startup
load_data()

# Helper functions
def calculate_person_balance(person_name):
    """Calculate total balance for a person"""
    person_transactions = [t for t in st.session_state.transactions if t['person'].lower() == person_name.lower()]
    total = sum(t['amount'] for t in person_transactions)
    return total, person_transactions

def get_all_persons():
    """Get list of all unique persons"""
    persons = list(set([t['person'] for t in st.session_state.transactions]))
    return sorted(persons, key=str.lower)

def format_amount(amount):
    """Format amount with + or - sign"""
    if amount > 0:
        return f"+${abs(amount):.2f}"
    elif amount < 0:
        return f"-${abs(amount):.2f}"
    else:
        return "$0.00"

def get_transaction_type(amount):
    """Get transaction type based on amount"""
    if amount > 0:
        return "You gave"
    else:
        return "You borrowed"

# Header
st.markdown("""
<h1 style='text-align: center; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: bold;'>
    💸 Friend Money Tracker
</h1>
<p style='text-align: center; color: #666; font-size: 1.2rem;'>
    Never forget who owes you and whom you owe!
</p>
""", unsafe_allow_html=True)

# Sidebar for adding transactions
with st.sidebar:
    st.markdown("## 💰 Add Transaction")
    
    with st.form("transaction_form", clear_on_submit=True):
        # Person selection or new person
        persons_list = get_all_persons()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            person_option = st.selectbox(
                "Select Person",
                ["➕ Add New Person"] + persons_list if persons_list else ["➕ Add New Person"]
            )
        
        if person_option == "➕ Add New Person":
            person_name = st.text_input("Person Name*", placeholder="Enter friend's name")
        else:
            person_name = person_option
        
        # Transaction type
        transaction_type = st.radio(
            "Transaction Type",
            ["💚 I gave money (They owe me)", "💔 I borrowed money (I owe them)"],
            index=0
        )
        
        # Amount
        amount = st.number_input(
            "Amount ($)*", 
            min_value=0.01, 
            step=0.01, 
            format="%.2f"
        )
        
        # Date
        transaction_date = st.date_input(
            "Date*", 
            value=date.today(), 
            max_value=date.today()
        )
        
        # Optional fields
        st.markdown("#### Optional Details")
        
        # Purpose/Comment
        purpose = st.text_area(
            "Purpose/Comments", 
            placeholder="e.g., Lunch money, Movie tickets, Loan for bike repair",
            height=60
        )
        
        # Is this a repayment?
        is_repayment = st.checkbox("This is a repayment of previous debt")
        
        # Submit button
        submitted = st.form_submit_button("💾 Add Transaction", use_container_width=True)
        
        if submitted:
            if person_name and amount > 0:
                # Determine actual amount (positive for given, negative for borrowed)
                if "gave money" in transaction_type:
                    actual_amount = amount
                else:
                    actual_amount = -amount
                
                transaction = {
                    'person': person_name,
                    'amount': actual_amount,
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'purpose': purpose,
                    'is_repayment': is_repayment,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                st.session_state.transactions.append(transaction)
                save_data()
                st.success(f"✅ Transaction added for {person_name}!")
                st.rerun()
            else:
                st.error("Please fill in all required fields!")
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.markdown("## 📊 Quick Stats")
    
    total_owed_to_me = sum(t['amount'] for t in st.session_state.transactions if t['amount'] > 0)
    total_i_owe = sum(abs(t['amount']) for t in st.session_state.transactions if t['amount'] < 0)
    net_balance = sum(t['amount'] for t in st.session_state.transactions)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("They Owe Me", f"${total_owed_to_me:.2f}")
    with col2:
        st.metric("I Owe", f"${total_i_owe:.2f}")
    
    if net_balance > 0:
        st.success(f"**Net Position:** +${net_balance:.2f}")
    elif net_balance < 0:
        st.error(f"**Net Position:** -${abs(net_balance):.2f}")
    else:
        st.info("**Net Position:** $0.00")
    
    st.markdown("---")
    
    # Clear all data
    if st.button("🗑️ Clear All Data", use_container_width=True):
        if st.checkbox("I'm sure I want to delete all data"):
            st.session_state.transactions = []
            st.session_state.show_person_details = {}
            save_data()
            st.rerun()

# Main content area
if st.session_state.transactions:
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_owed_to_me = sum(t['amount'] for t in st.session_state.transactions if t['amount'] > 0)
        st.metric("💚 Total Owed to Me", f"${total_owed_to_me:.2f}")
    
    with col2:
        total_i_owe = sum(abs(t['amount']) for t in st.session_state.transactions if t['amount'] < 0)
        st.metric("💔 Total I Owe", f"${total_i_owe:.2f}")
    
    with col3:
        net_balance = sum(t['amount'] for t in st.session_state.transactions)
        st.metric(
            "💰 Net Balance", 
            f"${abs(net_balance):.2f}",
            delta="You're owed" if net_balance > 0 else "You owe" if net_balance < 0 else "Settled"
        )
    
    with col4:
        num_people = len(get_all_persons())
        st.metric("👥 Total People", num_people)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["👥 By Person", "📋 All Transactions", "📊 Analytics", "📈 Summary"])
    
    with tab1:
        st.markdown("### 👥 Balance by Person")
        st.markdown("Click on any person to see detailed transactions")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox(
                "Show",
                ["All", "People who owe me", "People I owe", "Settled"]
            )
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Name", "Amount (High to Low)", "Amount (Low to High)", "Most Recent"]
            )
        with col3:
            search_person = st.text_input("🔍 Search Person", placeholder="Type name...")
        
        # Get all persons and their balances
        persons_data = []
        for person in get_all_persons():
            balance, transactions = calculate_person_balance(person)
            last_transaction = max(transactions, key=lambda x: x['timestamp'])['date'] if transactions else None
            persons_data.append({
                'name': person,
                'balance': balance,
                'transactions': transactions,
                'last_date': last_transaction
            })
        
        # Apply filters
        if search_person:
            persons_data = [p for p in persons_data if search_person.lower() in p['name'].lower()]
        
        if filter_type == "People who owe me":
            persons_data = [p for p in persons_data if p['balance'] > 0]
        elif filter_type == "People I owe":
            persons_data = [p for p in persons_data if p['balance'] < 0]
        elif filter_type == "Settled":
            persons_data = [p for p in persons_data if p['balance'] == 0]
        
        # Apply sorting
        if sort_by == "Name":
            persons_data.sort(key=lambda x: x['name'].lower())
        elif sort_by == "Amount (High to Low)":
            persons_data.sort(key=lambda x: x['balance'], reverse=True)
        elif sort_by == "Amount (Low to High)":
            persons_data.sort(key=lambda x: x['balance'])
        elif sort_by == "Most Recent":
            persons_data.sort(key=lambda x: x['last_date'] or '', reverse=True)
        
        # Display persons
        for person_data in persons_data:
            person = person_data['name']
            balance = person_data['balance']
            transactions = person_data['transactions']
            
            # Create expandable card for each person
            with st.expander(f"**{person}** - {format_amount(balance)}", expanded=st.session_state.show_person_details.get(person, False)):
                # Summary for this person
                col1, col2, col3 = st.columns(3)
                with col1:
                    if balance > 0:
                        st.markdown(f"<div class='owe-me'>📈 Owes you: ${balance:.2f}</div>", unsafe_allow_html=True)
                    elif balance < 0:
                        st.markdown(f"<div class='i-owe'>📉 You owe: ${abs(balance):.2f}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='neutral'>✅ Settled</div>", unsafe_allow_html=True)
                
                with col2:
                    st.metric("Total Transactions", len(transactions))
                
                with col3:
                    if transactions:
                        last_date = max(t['date'] for t in transactions)
                        st.metric("Last Transaction", last_date)
                
                # Transaction history
                st.markdown("#### 📜 Transaction History")
                
                # Sort transactions by date (newest first)
                sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
                
                for idx, trans in enumerate(sorted_transactions):
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
                    
                    with col1:
                        st.write(f"📅 {trans['date']}")
                    
                    with col2:
                        if trans['amount'] > 0:
                            st.success(f"✅ +${trans['amount']:.2f}")
                        else:
                            st.error(f"❌ -${abs(trans['amount']):.2f}")
                    
                    with col3:
                        trans_type = get_transaction_type(trans['amount'])
                        repay_tag = "🔄 (Repayment)" if trans.get('is_repayment', False) else ""
                        st.write(f"{trans_type} {repay_tag}")
                    
                    with col4:
                        if trans.get('purpose'):
                            st.write(f"💬 {trans['purpose'][:30]}...")
                            if len(trans['purpose']) > 30:
                                if st.button("View", key=f"view_{person}_{idx}"):
                                    st.info(trans['purpose'])
                    
                    with col5:
                        if st.button("🗑️", key=f"del_{person}_{idx}"):
                            st.session_state.transactions.remove(trans)
                            save_data()
                            st.rerun()
                    
                    st.divider()
                
                # Quick actions for this person
                st.markdown("#### ⚡ Quick Actions")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"💰 Add Payment", key=f"add_{person}"):
                        st.info(f"Use the sidebar to add a new transaction for {person}")
                with col2:
                    if balance != 0 and st.button(f"✅ Mark as Settled", key=f"settle_{person}"):
                        settlement = {
                            'person': person,
                            'amount': -balance,
                            'date': date.today().strftime('%Y-%m-%d'),
                            'purpose': "Full settlement",
                            'is_repayment': True,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        st.session_state.transactions.append(settlement)
                        save_data()
                        st.success(f"Marked as settled with {person}!")
                        st.rerun()
                with col3:
                    if st.button(f"📊 Export", key=f"export_{person}"):
                        df = pd.DataFrame(transactions)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"{person}_transactions.csv",
                            mime="text/csv"
                        )
    
    with tab2:
        st.markdown("### 📋 All Transactions")
        
        # Create DataFrame
        df = pd.DataFrame(st.session_state.transactions)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        
        # Display filters
        col1, col2, col3 = st.columns(3)
        with col1:
            date_filter = st.date_input(
                "Date Range",
                value=(df['date'].min().date(), df['date'].max().date()),
                max_value=date.today()
            )
        with col2:
            type_filter = st.selectbox(
                "Transaction Type",
                ["All", "Money Given", "Money Borrowed", "Repayments"]
            )
        with col3:
            person_filter = st.selectbox(
                "Filter by Person",
                ["All"] + get_all_persons()
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if len(date_filter) == 2:
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= date_filter[0]) & 
                (filtered_df['date'].dt.date <= date_filter[1])
            ]
        
        if type_filter == "Money Given":
            filtered_df = filtered_df[filtered_df['amount'] > 0]
        elif type_filter == "Money Borrowed":
            filtered_df = filtered_df[filtered_df['amount'] < 0]
        elif type_filter == "Repayments":
            filtered_df = filtered_df[filtered_df['is_repayment'] == True]
        
        if person_filter != "All":
            filtered_df = filtered_df[filtered_df['person'] == person_filter]
        
        # Display transactions
        for idx, row in filtered_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 1])
            
            with col1:
                st.write(f"**{row['person']}**")
            with col2:
                st.write(f"📅 {row['date'].strftime('%Y-%m-%d')}")
            with col3:
                if row['amount'] > 0:
                    st.success(f"+${row['amount']:.2f}")
                else:
                    st.error(f"-${abs(row['amount']):.2f}")
            with col4:
                purpose_text = row.get('purpose', 'No description')
                if row.get('is_repayment'):
                    purpose_text = f"🔄 {purpose_text}"
                st.write(purpose_text[:50] + "..." if len(purpose_text) > 50 else purpose_text)
            with col5:
                if st.button("🗑️", key=f"del_trans_{idx}"):
                    for i, t in enumerate(st.session_state.transactions):
                        if t['timestamp'] == row['timestamp']:
                            st.session_state.transactions.pop(i)
                            break
                    save_data()
                    st.rerun()
            
            st.divider()
    
    with tab3:
        st.markdown("### 📊 Analytics")
        
        df = pd.DataFrame(st.session_state.transactions)
        df['date'] = pd.to_datetime(df['date'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Money flow over time
            st.markdown("#### 💹 Money Flow Over Time")
            
            daily_flow = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
            daily_flow.columns = ['date', 'amount']
            daily_flow['cumulative'] = daily_flow['amount'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_flow['date'],
                y=daily_flow['cumulative'],
                mode='lines+markers',
                name='Net Position',
                line=dict(color='purple', width=3),
                fill='tozeroy',
                fillcolor='rgba(128, 0, 128, 0.2)'
            ))
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                title="Cumulative Net Position",
                xaxis_title="Date",
                yaxis_title="Amount ($)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top debtors/creditors
            st.markdown("#### 🏆 Top Balances")
            
            person_balances = []
            for person in get_all_persons():
                balance, _ = calculate_person_balance(person)
                person_balances.append({'Person': person, 'Balance': balance})
            
            balance_df = pd.DataFrame(person_balances)
            balance_df = balance_df.sort_values('Balance', ascending=False)
            
            # Separate positive and negative
            owe_me = balance_df[balance_df['Balance'] > 0].head(5)
            i_owe = balance_df[balance_df['Balance'] < 0].head(5)
            
            if not owe_me.empty:
                st.success("**People who owe me most:**")
                for _, row in owe_me.iterrows():
                    st.write(f"{row['Person']}: ${row['Balance']:.2f}")
                    st.progress(row['Balance'] / owe_me['Balance'].max())
            
            if not i_owe.empty:
                st.error("**People I owe most:**")
                for _, row in i_owe.iterrows():
                    st.write(f"{row['Person']}: ${abs(row['Balance']):.2f}")
                    st.progress(abs(row['Balance']) / abs(i_owe['Balance'].min()))
        
        # Transaction patterns
        st.markdown("#### 📈 Transaction Patterns")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Monthly summary
            df['month'] = df['date'].dt.to_period('M').astype(str)
            monthly_summary = df.groupby('month')['amount'].agg(['sum', 'count'])
            
            if not monthly_summary.empty:
                fig = px.bar(
                    monthly_summary.reset_index(),
                    x='month',
                    y='sum',
                    color='sum',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    title='Monthly Net Flow'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Transaction frequency by person
            person_freq = df['person'].value_counts().head(10)
            fig = px.pie(
                values=person_freq.values,
                names=person_freq.index,
                title='Transaction Frequency by Person'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Repayment rate
            total_trans = len(df)
            repayments = len(df[df['is_repayment'] == True])
            repayment_rate = (repayments / total_trans * 100) if total_trans > 0 else 0
            
            st.metric("Repayment Rate", f"{repayment_rate:.1f}%")
            st.progress(repayment_rate / 100)
            
            # Average transaction
            avg_given = df[df['amount'] > 0]['amount'].mean() if len(df[df['amount'] > 0]) > 0 else 0
            avg_borrowed = abs(df[df['amount'] < 0]['amount'].mean()) if len(df[df['amount'] < 0]) > 0 else 0
            
            st.metric("Avg Money Given", f"${avg_given:.2f}")
            st.metric("Avg Money Borrowed", f"${avg_borrowed:.2f}")
    
    with tab4:
        st.markdown("### 📈 Summary Report")
        
        # Generate summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📊 Overall Summary")
            
            # Create summary statistics
            total_transactions = len(st.session_state.transactions)
            total_people = len(get_all_persons())
            total_given = sum(t['amount'] for t in st.session_state.transactions if t['amount'] > 0)
            total_borrowed = sum(abs(t['amount']) for t in st.session_state.transactions if t['amount'] < 0)
            net_position = total_given - total_borrowed
            
            summary_text = f"""
            **📅 Tracking Period:** {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
            
            **💵 Financial Overview:**
            - Total money given out: **${total_given:.2f}**
            - Total money borrowed: **${total_borrowed:.2f}**
            - Net position: **{format_amount(net_position)}**
            
            **📊 Activity Summary:**
            - Total transactions: **{total_transactions}**
            - Number of people: **{total_people}**
            - Average transaction: **${(total_given + total_borrowed) / total_transactions:.2f}**
            
            **👥 People Summary:**
            """
            
            st.markdown(summary_text)
            
            # List all people with their status
            for person in get_all_persons():
                balance, transactions = calculate_person_balance(person)
                if balance > 0:
                    st.success(f"✅ {person}: Owes you ${balance:.2f} ({len(transactions)} transactions)")
                elif balance < 0:
                    st.error(f"❌ {person}: You owe ${abs(balance):.2f} ({len(transactions)} transactions)")
                else:
                    st.info(f"☑️ {person}: Settled ({len(transactions)} transactions)")
        
        with col2:
            st.markdown("#### 💡 Quick Insights")
            
            # Identify patterns
            if total_given > total_borrowed:
                st.info(f"💰 You're a net lender! You've given ${net_position:.2f} more than borrowed.")
            elif total_borrowed > total_given:
                st.warning(f"💳 You're a net borrower! You've borrowed ${abs(net_position):.2f} more than given.")
            else:
                st.success("✅ Perfect balance! Given and borrowed amounts are equal.")
            
            # Most active relationship
            if get_all_persons():
                most_active = max(get_all_persons(), key=lambda p: len([t for t in st.session_state.transactions if t['person'] == p]))
                st.info(f"🤝 Most active: {most_active}")
            
            # Export options
            st.markdown("#### 📥 Export Data")
            
            export_df = pd.DataFrame(st.session_state.transactions)
            csv = export_df.to_csv(index=False)
            
            st.download_button(
                label="📄 Download All Data (CSV)",
                data=csv,
                file_name=f"money_tracker_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

else:
    # Empty state
    st.markdown("""
    <div style='text-align: center; padding: 50px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 20px; margin: 20px;'>
        <h2 style='color: #4a5568;'>👋 Welcome to Your Money Tracker!</h2>
        <p style='font-size: 1.2rem; color: #718096; margin: 20px 0;'>
            Keep track of money you've lent to friends and money you've borrowed.<br>
            Never forget who owes you or whom you owe!
        </p>
        
        <div style='background: white; padding: 20px; border-radius: 15px; margin: 30px auto; max-width: 600px;'>
            <h3 style='color: #2d3748;'>🚀 How to Get Started:</h3>
            <ol style='text-align: left; color: #4a5568; font-size: 1.1rem;'>
                <li>Click the sidebar (left) to add your first transaction</li>
                <li>Enter your friend's name</li>
                <li>Choose if you gave or borrowed money</li>
                <li>Enter the amount and date</li>
                <li>Add optional notes about what it was for</li>
                <li>Click "Add Transaction" to save</li>
            </ol>
        </div>
        
        <div style='margin-top: 30px;'>
            <p style='color: #718096;'>
                <strong>Pro Tip:</strong> You can mark transactions as "repayments" when someone pays you back!
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💾 All data is automatically saved locally | 🔒 Your data stays private on your device</p>
    <p style='font-size: 0.9rem; margin-top: 10px;'>Made with ❤️ using Python & Streamlit</p>
</div>
""", unsafe_allow_html=True)