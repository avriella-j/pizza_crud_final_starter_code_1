# TODO: Make Pizza CRUD App Runnable

## Tasks to Complete:

- [x] 1. Fix confirmation.html template
  - [x] Change CSS reference from `style.css` to `styles.css`
  - [x] Change logo reference from `CRUD_Pizza_logo.jpg` to `CRUD_Pizza_logo.png`
  - [x] Change `order.order_date` to `display_date`
  - [x] Fix back link href to point to menu
  - [x] Add customer name display

- [x] 2. Update database schema and app.py
  - [x] Add `customer_name` column to Order table
  - [x] Update `save_order()` function to accept and save customer_name
  - [x] Update `get_order_details()` to retrieve customer_name
  - [x] Update `create_order()` route to get customer_name from form
  - [x] Update `confirmation()` route to pass customer_name to template

- [x] 3. Update .gitignore
  - [x] Add data/ directory
  - [x] Add virtual environment folders
  - [x] Add Python cache files

- [x] 4. Test the application
  - [x] Run the app - Successfully running on http://127.0.0.1:5000
  - [ ] Test order creation - Ready for manual testing
  - [ ] Verify confirmation page - Ready for manual testing
