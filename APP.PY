from flask import Flask, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'digital_saathi_secret_key'

DATA_FILE = 'business_data.json'

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'business_name': 'My Business',
        'products': [],
        'customers': [],
        'bills': []
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check_expiry_alerts(products):
    """Check for products nearing expiry"""
    today = datetime.now().date()
    expired = []
    expiring_soon = []
    
    for product in products:
        if 'expiry_date' in product and product['expiry_date']:
            try:
                expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d").date()
                days_until_expiry = (expiry_date - today).days
                
                if days_until_expiry < 0:
                    expired.append(product)
                elif days_until_expiry <= 7:  # Alert 7 days before
                    expiring_soon.append((product, days_until_expiry))
            except:
                continue
    
    return expired, expiring_soon

def get_expiry_alerts_html(products):
    """Generate HTML for expiry alerts"""
    expired, expiring_soon = check_expiry_alerts(products)
    
    if not expired and not expiring_soon:
        return ''
    
    alerts_html = '<div class="alert alert-warning">'
    alerts_html += '<h5>🚨 Product Expiry Alerts</h5>'
    
    if expired:
        alerts_html += '<p><strong>❌ EXPIRED PRODUCTS:</strong></p><ul>'
        for product in expired:
            expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            alerts_html += f'<li>{product["name"]} - Expired on {expiry_date}</li>'
        alerts_html += '</ul>'
    
    if expiring_soon:
        alerts_html += '<p><strong>⚠️ EXPIRING SOON (within 7 days):</strong></p><ul>'
        for product, days in expiring_soon:
            expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            alerts_html += f'<li>{product["name"]} - {days} days left (Expires: {expiry_date})</li>'
        alerts_html += '</ul>'
    
    alerts_html += '</div>'
    return alerts_html

@app.route('/')
def index():
    data = load_data()
    product_count = len(data['products'])
    customer_count = len(data['customers'])
    bill_count = len(data['bills'])
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Digital Saathi</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .stat-card {{ background: white; border-radius: 15px; padding: 20px; margin: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">🌟 Digital Saathi</a>
            </div>
        </nav>

        <div class="container mt-5">
            <div class="row">
                <div class="col-md-8 mx-auto text-center">
                    <h1 class="text-white">Welcome to Digital Saathi</h1>
                    <p class="text-white">Your Digital Business Companion</p>
                    
                    <div class="row mt-5">
                        <div class="col-md-3"><div class="stat-card"><h3>{product_count}</h3><p>Products</p></div></div>
                        <div class="col-md-3"><div class="stat-card"><h3>{customer_count}</h3><p>Customers</p></div></div>
                        <div class="col-md-3"><div class="stat-card"><h3>{bill_count}</h3><p>Bills</p></div></div>
                        <div class="col-md-3"><div class="stat-card"><h3>GST</h3><p>Compliant</p></div></div>
                    </div>

                    <div class="row mt-5">
                        <div class="col-md-6">
                            <a href="/business" class="btn btn-primary btn-lg w-100">🏢 Business Dashboard</a>
                        </div>
                        <div class="col-md-6">
                            <a href="/customer" class="btn btn-success btn-lg w-100">👥 Customer Portal</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/business')
def business_dashboard():
    data = load_data()
    business_name = data['business_name']
    product_count = len(data['products'])
    customer_count = len(data['customers'])
    bill_count = len(data['bills'])
    
    # Expiry alerts
    expiry_alerts = get_expiry_alerts_html(data['products'])
    
    # Generate products HTML with expiry info
    if data['products']:
        products_html = '<table class="table"><tr><th>Name</th><th>Price</th><th>Stock</th><th>GST</th><th>Expiry</th><th>Status</th></tr>'
        for product in data['products']:
            expiry_info = 'Not set'
            status_badge = ''
            
            if 'expiry_date' in product and product['expiry_date']:
                expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d")
                today = datetime.now().date()
                days_until = (expiry_date.date() - today).days
                expiry_info = expiry_date.strftime("%d-%m-%Y")
                
                if days_until < 0:
                    status_badge = '<span class="badge bg-danger">Expired</span>'
                elif days_until <= 7:
                    status_badge = f'<span class="badge bg-warning">{days_until}d left</span>'
                else:
                    status_badge = '<span class="badge bg-success">OK</span>'
            
            products_html += f'<tr><td>{product["name"]}</td><td>₹{product["price"]}</td><td>{product["quantity"]}</td><td>{product["gst_rate"]}%</td><td>{expiry_info}</td><td>{status_badge}</td></tr>'
        products_html += '</table>'
    else:
        products_html = '<p>No products yet</p>'
    
    # Generate customers HTML
    if data['customers']:
        customers_html = '<table class="table"><tr><th>Name</th><th>Phone</th><th>Email</th></tr>'
        for customer in data['customers']:
            customers_html += f'<tr><td>{customer["name"]}</td><td>{customer["phone"]}</td><td>{customer["email"] or "N/A"}</td></tr>'
        customers_html += '</table>'
    else:
        customers_html = '<p>No customers yet</p>'

    # Generate bills HTML
    if data['bills']:
        bills_html = '<table class="table"><tr><th>Bill No</th><th>Customer</th><th>Date</th><th>Total</th><th>Action</th></tr>'
        for bill in data['bills'][-5:]:
            bills_html += f'<tr><td>{bill["bill_number"]}</td><td>{bill["customer_name"]}</td><td>{bill["date"]}</td><td>₹{bill["total_amount"]}</td><td><a href="/view_bill/{bill["id"]}" class="btn btn-sm btn-info">View</a></td></tr>'
        bills_html += '</table>'
    else:
        bills_html = '<p>No bills generated yet</p>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Business Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">🌟 Digital Saathi</a>
                <a class="text-white" href="/customer">Customer View</a>
            </div>
        </nav>

        <div class="container mt-4">
            <h1>🏢 Business Dashboard</h1>
            <p>Welcome to {business_name}</p>

            {expiry_alerts}

            <div class="row mb-4">
                <div class="col-md-3">
                    <a href="/add_product" class="btn btn-primary w-100">📦 Add Product</a>
                </div>
                <div class="col-md-3">
                    <button class="btn btn-success w-100" data-bs-toggle="modal" data-bs-target="#customerModal">👥 Add Customer</button>
                </div>
                <div class="col-md-3">
                    <a href="/create_bill" class="btn btn-warning w-100">🧾 Create Bill</a>
                </div>
                <div class="col-md-3">
                    <a href="/expiry_management" class="btn btn-danger w-100">⏰ Expiry Mgmt</a>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header"><h5>📦 Products ({product_count})</h5></div>
                <div class="card-body">
                    {products_html}
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header"><h5>👥 Customers ({customer_count})</h5></div>
                <div class="card-body">
                    {customers_html}
                </div>
            </div>

            <div class="card">
                <div class="card-header"><h5>🧾 Recent Bills ({bill_count})</h5></div>
                <div class="card-body">
                    {bills_html}
                </div>
            </div>
        </div>

        <div class="modal fade" id="customerModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Customer</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" action="/add_customer">
                        <div class="modal-body">
                            <input type="text" name="name" class="form-control mb-2" placeholder="Name" required>
                            <input type="tel" name="phone" class="form-control mb-2" placeholder="Phone" required>
                            <input type="email" name="email" class="form-control" placeholder="Email">
                        </div>
                        <div class="modal-footer">
                            <button type="submit" class="btn btn-primary">Add Customer</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''

@app.route('/customer')
def customer_dashboard():
    data = load_data()
    business_name = data['business_name']
    
    # Generate products HTML
    if data['products']:
        products_html = ''
        for product in data['products']:
            final_price = product['price'] * (1 + product['gst_rate']/100)
            
            # Add expiry warning for customers
            expiry_warning = ''
            if 'expiry_date' in product and product['expiry_date']:
                expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d")
                today = datetime.now().date()
                days_until = (expiry_date.date() - today).days
                if days_until <= 7:
                    expiry_warning = f'<div class="alert alert-warning py-1 mt-2"><small>⏰ Expires soon: {expiry_date.strftime("%d-%m-%Y")}</small></div>'
            
            products_html += f'''
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5>{product["name"]}</h5>
                        <p>Price: ₹{product["price"]}</p>
                        <p>GST: {product["gst_rate"]}%</p>
                        <p>Final: ₹{final_price:.2f}</p>
                        <p>Stock: {product["quantity"]}</p>
                        {expiry_warning}
                    </div>
                </div>
            </div>
            '''
    else:
        products_html = '<div class="col-12"><p>No products available</p></div>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Portal</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-success">
            <div class="container">
                <a class="navbar-brand" href="/">🌟 Digital Saathi</a>
                <a class="text-white" href="/business">Business View</a>
            </div>
        </nav>

        <div class="container mt-4">
            <h1>👥 Customer Portal</h1>
            <p>Welcome to {business_name}</p>

            <div class="row">
                {products_html}
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        data = load_data()
        try:
            name = request.form['name']
            price = float(request.form['price'])
            quantity = int(request.form['quantity'])
            gst_rate = float(request.form['gst_rate'])
            expiry_date = request.form.get('expiry_date', '')
            
            new_product = {
                'id': len(data['products']) + 1,
                'name': name,
                'price': price,
                'quantity': quantity,
                'gst_rate': gst_rate,
                'added_date': datetime.now().strftime("%Y-%m-%d")
            }
            
            if expiry_date:
                new_product['expiry_date'] = expiry_date
            
            data['products'].append(new_product)
            save_data(data)
            return redirect('/business')
        except Exception as e:
            return f'Error: {str(e)}'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Product</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/business">← Back to Dashboard</a>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header"><h4>Add Product</h4></div>
                        <div class="card-body">
                            <form method="POST">
                                <input type="text" name="name" class="form-control mb-2" placeholder="Product Name" required>
                                <input type="number" name="price" class="form-control mb-2" placeholder="Price" step="0.01" required>
                                <input type="number" name="quantity" class="form-control mb-2" placeholder="Quantity" required>
                                <select name="gst_rate" class="form-control mb-2" required>
                                    <option value="0">0% GST</option>
                                    <option value="5">5% GST</option>
                                    <option value="12">12% GST</option>
                                    <option value="18" selected>18% GST</option>
                                    <option value="28">28% GST</option>
                                </select>
                                <input type="date" name="expiry_date" class="form-control mb-2" placeholder="Expiry Date (Optional)">
                                <small class="text-muted">Leave empty if no expiry date</small>
                                <button type="submit" class="btn btn-primary w-100 mt-2">Add Product</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = load_data()
    try:
        name = request.form['name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        
        new_customer = {
            'id': len(data['customers']) + 1,
            'name': name,
            'phone': phone,
            'email': email
        }
        
        data['customers'].append(new_customer)
        save_data(data)
        return redirect('/business')
    except Exception as e:
        return f'Error: {str(e)}'

@app.route('/expiry_management')
def expiry_management():
    data = load_data()
    
    expired, expiring_soon = check_expiry_alerts(data['products'])
    
    expired_html = ''
    if expired:
        expired_html = '<div class="card border-danger mb-4"><div class="card-header bg-danger text-white"><h5>❌ EXPIRED PRODUCTS</h5></div><div class="card-body"><ul>'
        for product in expired:
            expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            expired_html += f'<li><strong>{product["name"]}</strong> - Expired on {expiry_date} (Stock: {product["quantity"]})</li>'
        expired_html += '</ul></div></div>'
    
    expiring_html = ''
    if expiring_soon:
        expiring_html = '<div class="card border-warning mb-4"><div class="card-header bg-warning"><h5>⚠️ EXPIRING SOON (within 7 days)</h5></div><div class="card-body"><ul>'
        for product, days in expiring_soon:
            expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d").strftime("%d-%m-%Y")
            expiring_html += f'<li><strong>{product["name"]}</strong> - {days} days left (Expires: {expiry_date}, Stock: {product["quantity"]})</li>'
        expiring_html += '</ul></div></div>'
    
    # Products with expiry dates
    products_with_expiry = [p for p in data['products'] if 'expiry_date' in p and p['expiry_date']]
    expiry_table = ''
    if products_with_expiry:
        expiry_table = '<div class="card"><div class="card-header"><h5>All Products with Expiry Dates</h5></div><div class="card-body"><table class="table"><tr><th>Product</th><th>Expiry Date</th><th>Days Left</th><th>Stock</th><th>Action</th></tr>'
        for product in products_with_expiry:
            expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d")
            today = datetime.now().date()
            days_left = (expiry_date.date() - today).days
            
            status_badge = ''
            if days_left < 0:
                status_badge = '<span class="badge bg-danger">Expired</span>'
            elif days_left <= 7:
                status_badge = f'<span class="badge bg-warning">{days_left} days</span>'
            else:
                status_badge = f'<span class="badge bg-success">{days_left} days</span>'
            
            expiry_table += f'<tr><td>{product["name"]}</td><td>{expiry_date.strftime("%d-%m-%Y")}</td><td>{status_badge}</td><td>{product["quantity"]}</td><td><a href="/update_expiry/{product["id"]}" class="btn btn-sm btn-outline-primary">Update</a></td></tr>'
        expiry_table += '</table></div></div>'
    else:
        expiry_table = '<div class="alert alert-info">No products with expiry dates set.</div>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Expiry Management</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-danger">
            <div class="container">
                <a class="navbar-brand" href="/business">← Back to Dashboard</a>
            </div>
        </nav>

        <div class="container mt-4">
            <h1>⏰ Expiry Date Management</h1>
            <p>Monitor and manage product expiry dates</p>
            
            {expired_html}
            {expiring_html}
            {expiry_table}
        </div>
    </body>
    </html>
    '''

@app.route('/update_expiry/<int:product_id>', methods=['GET', 'POST'])
def update_expiry(product_id):
    data = load_data()
    product = next((p for p in data['products'] if p['id'] == product_id), None)
    
    if not product:
        return "Product not found"
    
    if request.method == 'POST':
        new_expiry = request.form.get('expiry_date', '')
        if new_expiry:
            product['expiry_date'] = new_expiry
        else:
            # Remove expiry date if empty
            if 'expiry_date' in product:
                del product['expiry_date']
        
        save_data(data)
        return redirect('/expiry_management')
    
    current_expiry = product.get('expiry_date', '')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Update Expiry</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/expiry_management">← Back to Expiry Management</a>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h4>Update Expiry Date</h4>
                        </div>
                        <div class="card-body">
                            <p><strong>Product:</strong> {product['name']}</p>
                            <form method="POST">
                                <div class="mb-3">
                                    <label class="form-label">Expiry Date</label>
                                    <input type="date" name="expiry_date" class="form-control" value="{current_expiry}">
                                    <small class="text-muted">Leave empty to remove expiry date</small>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Update Expiry</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# [Include all the previous bill-related routes from the last version here]
# create_bill, view_bills, view_bill routes remain the same as in previous version

@app.route('/create_bill', methods=['GET', 'POST'])
def create_bill():
    data = load_data()
    
    if request.method == 'POST':
        try:
            customer_id = int(request.form['customer_id'])
            customer = next((c for c in data['customers'] if c['id'] == customer_id), None)
            
            if not customer:
                return "Customer not found"
            
            # Get selected products
            bill_items = []
            total_amount = 0
            total_gst = 0
            
            for product in data['products']:
                quantity_str = request.form.get(f'quantity_{product["id"]}', '0')
                if quantity_str and int(quantity_str) > 0:
                    quantity = int(quantity_str)
                    if product['quantity'] >= quantity:
                        item_total = product['price'] * quantity
                        item_gst = (item_total * product['gst_rate']) / 100
                        
                        bill_items.append({
                            'product_name': product['name'],
                            'quantity': quantity,
                            'price': product['price'],
                            'gst_rate': product['gst_rate'],
                            'gst_amount': item_gst,
                            'total': item_total
                        })
                        
                        total_amount += item_total
                        total_gst += item_gst
                        
                        # Update stock
                        product['quantity'] -= quantity
            
            if bill_items:
                final_total = total_amount + total_gst
                
                new_bill = {
                    'id': len(data['bills']) + 1,
                    'bill_number': f"DS{len(data['bills']) + 1:03d}",
                    'customer_name': customer['name'],
                    'date': datetime.now().strftime("%d-%m-%Y %H:%M"),
                    'items': bill_items,
                    'subtotal': total_amount,
                    'total_gst': total_gst,
                    'total_amount': final_total
                }
                
                data['bills'].append(new_bill)
                save_data(data)
                return redirect(f'/view_bill/{new_bill["id"]}')
            else:
                return "No items selected or insufficient stock"
                
        except Exception as e:
            return f'Error creating bill: {str(e)}'
    
    # GET request - show bill creation form
    products_options = ''
    for product in data['products']:
        # Add expiry warning
        expiry_warning = ''
        if 'expiry_date' in product and product['expiry_date']:
            expiry_date = datetime.strptime(product['expiry_date'], "%Y-%m-%d")
            today = datetime.now().date()
            days_until = (expiry_date.date() - today).days
            if days_until <= 7:
                expiry_warning = f'<span class="badge bg-warning ms-2">Expires: {expiry_date.strftime("%d-%m-%Y")}</span>'
        
        products_options += f'''
        <div class="row mb-2">
            <div class="col-md-6">{product["name"]} - ₹{product["price"]} (GST: {product["gst_rate"]}%) {expiry_warning}</div>
            <div class="col-md-3">Stock: {product["quantity"]}</div>
            <div class="col-md-3">
                <input type="number" name="quantity_{product["id"]}" class="form-control" min="0" max="{product["quantity"]}" value="0">
            </div>
        </div>
        '''
    
    customers_options = ''
    for customer in data['customers']:
        customers_options += f'<option value="{customer["id"]}">{customer["name"]} - {customer["phone"]}</option>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Bill</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/business">← Back to Dashboard</a>
            </div>
        </nav>

        <div class="container mt-4">
            <h2>🧾 Create New Bill</h2>
            
            <form method="POST">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Select Customer</h5>
                    </div>
                    <div class="card-body">
                        <select name="customer_id" class="form-control" required>
                            <option value="">Choose a customer...</option>
                            {customers_options}
                        </select>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h5>Select Products & Quantities</h5>
                    </div>
                    <div class="card-body">
                        {products_options}
                    </div>
                </div>

                <div class="mt-4">
                    <button type="submit" class="btn btn-success btn-lg w-100">Generate Bill</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/view_bills')
def view_bills():
    data = load_data()
    
    if data['bills']:
        bills_html = '<table class="table"><tr><th>Bill No</th><th>Customer</th><th>Date</th><th>Total</th><th>GST</th><th>Action</th></tr>'
        for bill in data['bills']:
            bills_html += f'<tr><td>{bill["bill_number"]}</td><td>{bill["customer_name"]}</td><td>{bill["date"]}</td><td>₹{bill["total_amount"]}</td><td>₹{bill["total_gst"]}</td><td><a href="/view_bill/{bill["id"]}" class="btn btn-sm btn-info">View</a></td></tr>'
        bills_html += '</table>'
    else:
        bills_html = '<p>No bills generated yet</p>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Bills</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/business">← Back to Dashboard</a>
            </div>
        </nav>

        <div class="container mt-4">
            <h2>📋 All Bills</h2>
            {bills_html}
        </div>
    </body>
    </html>
    '''

@app.route('/view_bill/<int:bill_id>')
def view_bill(bill_id):
    data = load_data()
    bill = next((b for b in data['bills'] if b['id'] == bill_id), None)
    
    if not bill:
        return "Bill not found"
    
    items_html = ''
    for item in bill['items']:
        items_html += f'''
        <tr>
            <td>{item['product_name']}</td>
            <td>{item['quantity']}</td>
            <td>₹{item['price']}</td>
            <td>{item['gst_rate']}%</td>
            <td>₹{item['gst_amount']:.2f}</td>
            <td>₹{item['total']}</td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bill {bill['bill_number']}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, .15); }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/business">← Back to Dashboard</a>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="invoice-box">
                <div class="text-center mb-4">
                    <h1>🌟 Digital Saathi</h1>
                    <h3>TAX INVOICE</h3>
                </div>
                
                <div class="row mb-4">
                    <div class="col-md-6">
                        <strong>Business:</strong> {data['business_name']}<br>
                    </div>
                    <div class="col-md-6 text-end">
                        <strong>Bill No:</strong> {bill['bill_number']}<br>
                        <strong>Date:</strong> {bill['date']}
                    </div>
                </div>
                
                <div class="row mb-4">
                    <div class="col-12">
                        <strong>Customer:</strong> {bill['customer_name']}
                    </div>
                </div>
                
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Qty</th>
                            <th>Price</th>
                            <th>GST %</th>
                            <th>GST Amt</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr>
                            <td colspan="4"></td>
                            <td><strong>Subtotal:</strong></td>
                            <td><strong>₹{bill['subtotal']:.2f}</strong></td>
                        </tr>
                        <tr>
                            <td colspan="4"></td>
                            <td><strong>Total GST:</strong></td>
                            <td><strong>₹{bill['total_gst']:.2f}</strong></td>
                        </tr>
                        <tr>
                            <td colspan="4"></td>
                            <td><strong>Grand Total:</strong></td>
                            <td><strong>₹{bill['total_amount']:.2f}</strong></td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="text-center mt-4">
                    <p>Thank you for your business! 🙏</p>
                    <p><small>Generated by Digital Saathi - Viksit Bharat Buildathon Project</small></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        save_data(load_data())
    app.run(debug=True, host='0.0.0.0', port=5000)