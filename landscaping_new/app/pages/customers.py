"""
Customers Page

Handles customer management functionality.
"""
from __future__ import annotations
import streamlit as st
from database.queries.customers import list_customers, create_customer, get_customer, update_customer

def render_customers_page() -> None:
    """Render the customers page."""
    st.title("Customer Management")
    
    # Tabs for different customer operations
    tab1, tab2, tab3 = st.tabs(["View Customers", "Add Customer", "Edit Customer"])
    
    with tab1:
        st.subheader("All Customers")
        try:
            customers = list_customers()
            if customers:
                for customer in customers:
                    with st.expander(f"{customer['name']} - {customer['email']}"):
                        col1, col2, col3 = st.columns(3)
                        col1.write(f"**ID:** {customer['id']}")
                        col2.write(f"**Phone:** {customer['phone'] or 'N/A'}")
                        col3.write(f"**Status:** {'Active' if customer['is_active'] else 'Inactive'}")
                        
                        if st.button(f"Select Customer {customer['id']}", key=f"select_{customer['id']}"):
                            st.session_state.selected_customer = customer
                            st.rerun()
            else:
                st.info("No customers found. Add a customer using the 'Add Customer' tab.")
        except Exception as e:
            st.error(f"Error loading customers: {str(e)}")
    
    with tab2:
        st.subheader("Add New Customer")
        with st.form("add_customer_form"):
            name = st.text_input("Customer Name*", help="Enter the customer's full name")
            email = st.text_input("Email Address", help="Enter the customer's email address")
            phone = st.text_input("Phone Number", help="Enter the customer's phone number")
            address = st.text_area("Address", help="Enter the customer's address")
            
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                if name:
                    try:
                        customer = create_customer(name=name, email=email, phone=phone, address=address)
                        if customer:
                            st.success(f"Customer '{name}' added successfully with ID: {customer['id']}")
                        else:
                            st.error("Failed to add customer")
                    except Exception as e:
                        st.error(f"Error adding customer: {str(e)}")
                else:
                    st.error("Customer name is required")
    
    with tab3:
        st.subheader("Edit Customer")
        if 'selected_customer' in st.session_state:
            customer = st.session_state.selected_customer
            st.write(f"Editing customer: **{customer['name']}**")
            
            with st.form("edit_customer_form"):
                name = st.text_input("Customer Name", value=customer['name'])
                email = st.text_input("Email Address", value=customer['email'] or "")
                phone = st.text_input("Phone Number", value=customer['phone'] or "")
                address = st.text_area("Address", value=customer['address'] or "")
                is_active = st.checkbox("Active", value=customer['is_active'])
                
                submitted = st.form_submit_button("Update Customer")
                if submitted:
                    try:
                        success = update_customer(
                            customer['id'],
                            name=name,
                            email=email,
                            phone=phone,
                            address=address,
                            is_active=is_active
                        )
                        if success:
                            st.success("Customer updated successfully")
                            # Refresh the customer data
                            updated_customer = get_customer(customer['id'])
                            if updated_customer:
                                st.session_state.selected_customer = updated_customer
                        else:
                            st.error("Failed to update customer")
                    except Exception as e:
                        st.error(f"Error updating customer: {str(e)}")
        else:
            st.info("Select a customer from the 'View Customers' tab to edit.")