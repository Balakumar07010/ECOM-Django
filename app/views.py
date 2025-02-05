from django.shortcuts import render,redirect
from .models import *
import gridfs
import base64
import random
import string

user.update_many({"user_flag": {"$exists": False}}, {"$set": {"user_flag": False}})

def userLogin(req):
    if req.method=='POST':
        uname = req.POST['user_email']
        upass = req.POST['user_pass']
        # print(uname,upass)
        if uname and upass:
            a=user.find_one({"email":uname})
            # print(a)
            if a == None:
                message = "Please register this email then login"
                print("failed")
                return render(req, "userLogin.html", {"emailDup":message})
            elif uname == a.get("email") and upass == a.get("pass"):
                user.update_one({'email':uname}, {"$set":{'user_flag':"true"}})
                userFLAG = a.get("user_flag")
                req.session["email"]=uname
                print("success", userFLAG)
                v=list(products.find({}))
                fs = gridfs.GridFS(dbb)
                for product in v: 
                    if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                        try:
                            f1 = fs.get(product['image'])  # Get the image file from GridFS
                            img_data = f1.read()  # Read the image data
                            product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                        except Exception as e:
                            print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                            product['image_data'] = None  # Handle missing or invalid images
                return redirect(home)
            else:
                print("Password Wrong")
                message = "Enter a Correct Password";flag = True
                return render(req, "userLogin.html", {"passValid":message, "flagVal":flag})
    return render(req, "userLogin.html")
def userReg(request):
    # print(request.method)
    if request.method=='POST':
        user_details={}  
        user_details['username']=request.POST['user_name']
        user_details['email']=request.POST['user_email']
        user_details['address']=request.POST['user_address']
        user_details['pass']=request.POST['user_password']
        user_details['user_flag']="false"
        validEmail = request.POST['user_email']
        # print(validEmail)
        checkEmail = user.find_one({"email":validEmail})
        # print(checkEmail) 
        if checkEmail != None:
            message = "Email already exists"
            print("Email already exists")
            return render(request, "register.html", {"emailDup":message})
        else:
            user.insert_one(user_details) 
            # print(user_details)
            return redirect(userLogin) 
    return render(request,"register.html")
def user_profile(request):  
    u_name=request.session.get('email',None)
    v=[]
    v=list(user.find({"email":u_name}))
    
    # user_data = user.find_one({"email":u_name}),
    if request.method=='POST':
        userUpdate={}
        userUpdate['username']=request.POST['username']
        userUpdate['email']=request.POST['useremail']
        userUpdate['address']=request.POST['address']
        userUpdate['contact']=request.POST['contact']
        userUpdate['gender']=request.POST['gender']
        userUpdate['dob']=request.POST['dob']
        user.update_one({'email': userUpdate['email']}, {'$set': userUpdate})
        print("update")
        # print(userUpdate)
        return redirect(user_profile)
    return render(request,"userprofile.html",{"ob":v[0]})
def dashboard(req):
    return render(req,"dashboard.html")

def generate_unique_product_id(category, product_name, collection):
    # Extract the first three characters of category and product name
    category_part = (category[:3] if len(category) >= 3 else category).lower()
    product_part = (product_name[:3] if len(product_name) >= 3 else product_name).lower()
    
    # Start with a base unique value
    counter = 1
    unique_part = f"{counter:04d}"  # Format as a 4-digit number (e.g., 0001)
    product_id = f"{category_part}-{product_part}-{unique_part}"
    
    # Check for duplicates in the database and increment the counter
    while collection.find_one({"ProductId": product_id}):
        counter += 1
        unique_part = f"{counter:04d}"
        product_id = f"{category_part}-{product_part}-{unique_part}"

    return product_id

def addProducts(request):
    if request.method == 'POST':
        # Gather user details
        img = request.FILES['image']
        fs = gridfs.GridFS(dbb)  # Initialize GridFS
        fs_id = fs.put(img, filename=img.name)  # Store the image in GridFS
        
        seller_email = request.session.get('seller_email', None)
        
        category = request.POST.get('product-categories')
        product_name = request.POST.get('Product-name')
        
        # Generate unique Product ID
        product_id = generate_unique_product_id(category, product_name, products)  # Pass the collection
        color_value = request.POST.get('Color', '').strip()  # Get the color and strip whitespace
        price=request.POST.get('Price')
        price = int(price)
# Convert the color value to lowercase
        color_value_lower = color_value.lower()
        
        user_details = {
            'categories': category,
            'Product_name': product_name,
            'Quantity': request.POST.get('Quantity'),
            'Description': request.POST.get('Description'),
            'ProductId': product_id,
            'Price': price,
            'color': color_value_lower,
            'weight': request.POST.get('Weight'),
            'image': fs_id,
            'email': seller_email,
        }
        
        # Insert product details into MongoDB
        products.insert_one(user_details)

        # Optionally, redirect to another page (e.g., the products list page)
        return redirect(addProducts)

    return render(request, "addProducts.html")
def myProducts(req):
    v=[]
    seller_email = req.session.get('seller_email', None)
    v=list(products.find({'email':seller_email}))
    fs = gridfs.GridFS(dbb)
    # print(v)
    for product in v: 
        if 'image' in product:  # Ensure 'image' key exists in the product dictionary
            try:
                f1 = fs.get(product['image'])  # Get the image file from GridFS
                img_data = f1.read()  # Read the image data
                product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
            except Exception as e:
                print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                product['image_data'] = None  # Handle missing or invalid images
    return render(req,"myProduct.html",{'ob':v})
   
def salesReport(req):
    return render(req,"salesReport.html")
def sellerLogin(req):
    global s
    # print(req.method)
    if req.method=='POST':
        s_email = req.POST['seller_email']
        s_pass = req.POST['seller_password']
        print(s_email,s_pass)
        if s_email and s_pass:
            s=seller.find_one({"seller_email":s_email})
            if s == None:
                message = "Please register this email then login"
                print("failed")
                return render(req, "sellerLogin.html", {"emailDup":message})
            elif s_email == s.get("seller_email") and s_pass == s.get("seller_password"):
                req.session['seller_email'] = s_email
                print("success")
                return redirect(dashboard)
            else:
                print("Password Wrong")
                message = "Enter a Correct Password";flag = True
                return render(req, "sellerLogin.html", {"passValid":message, "flagVal":flag})
    return render(req, "sellerLogin.html")
def sellerProfile(req):
    semail=req.session.get('seller_email',None)
    sellerData=[]
    sellerData=list(seller.find({'seller_email':semail}))
    # print(req.method)

    if req.method=='POST':
        sellerUpdate={}
        sellerUpdate['shop_name']=req.POST['shop-name']
        sellerUpdate['seller_email']=req.POST['email-id']
        sellerUpdate['seller_address']=req.POST['address']
        sellerUpdate['seller_contact']=req.POST['contact']
        sellerUpdate['product_categories'] = req.POST['product-categories']
        sellerUpdate['gst_number']=req.POST['gst-number']
        seller.update_one({'seller_email': sellerUpdate['seller_email']}, {'$set': sellerUpdate})
        print("update")
        # print(sellerUpdate)
        return redirect(sellerProfile)
    return render(req,'profile.html',{"ob":sellerData})
def sellerRegister(request):
    # print(request.method)
    if request.method=='POST':
        seller_details={}  
        seller_details['sellerName']=request.POST['seller_name']
        seller_details['seller_email']=request.POST['seller_email']
        seller_details['seller_address']=request.POST['seller_address']
        seller_details['shop_name']=request.POST['shop_name']
        seller_details['seller_password']=request.POST['seller_password']
        validEmail = request.POST['seller_email']
        # print(validEmail)
        checkEmail = seller.find_one({"seller_email":validEmail})
        # print(checkEmail) 
        if checkEmail != None:
            message = "Email already exists"
            print("Email already exists")
            return render(request, "sellerRegister.html", {"emailDup":message})
        else:
            seller.insert_one(seller_details) 
            print(seller_details)
            return redirect(sellerLogin) 
    return render(request,"sellerRegister.html")

def homePage(req):
    return redirect(home)

def updateitem(request):
    # print("Method",request.method) 
    if request.method=='POST':
        seller_email = request.session.get('seller_email', None)
        product_id = request.POST.get('ProductId')
        img = request.FILES.get('image')
        fs = gridfs.GridFS(dbb)  # Initialize GridFS
        fs_id = fs.put(img, filename =img.name)  # Store the image in GridFS
        # print("product_id",product_id)
        user_details = {
            'categories': request.POST.get('product-categories'),
            'Product_name': request.POST.get('Product-name'),
            'Quantity': request.POST.get('Quantity'),
            'Description': request.POST.get('Description'),
            'ProductId': request.POST.get('ProductId'),
            'Price': request.POST.get('Price'),
            'image': fs_id,
        }
        # print(user_details)
        products.update_one({'ProductId':product_id}, {"$set": user_details})
        return redirect(myProducts)
    return render(request,"myProduct.html")

def deleteitem(request, ProductId):
        products.delete_one({'ProductId':ProductId})
        return redirect(myProducts)
    # return render(request,"myProduct.html")
def product(request, productId):
    email = request.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        print(email)
        print(productId)
        v =[]
        productList=[]
        productList = list(products.find({}))
        v=list(products.find({"ProductId":productId}))
        # print(productList)
        fs = gridfs.GridFS(dbb)
        for product in v: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        for product in productList: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(request,"products.html",{"item":v,"products":productList ,'ob':userDetails[0]})
    else:
        print(productId)
        v =[]
        productList=[]
        productList = list(products.find({}))
        v=list(products.find({"ProductId":productId}))
        # print(productList)
        fs = gridfs.GridFS(dbb)
        for product in v: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        for product in productList: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(request,"products.html",{"item":v,"products":productList })


def cart(request,productId):
    email = request.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v =[]
        v=list(products.find({"ProductId":productId}))
        fs = gridfs.GridFS(dbb)
        for productt in v: 
            # print("product Details : ",product)
            if 'image' in productt:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(productt['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    productt['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {productt.get('_id')}: {e}")  # Log any error
                    productt['image_data'] = None  # Handle missing or invalid images
        # v[0]["email"]=email
        # print(v)
        # print(v[0]['Product_name'],len(v))
        # v[0].update({'email':email})
        product_details = {
            'Product_name': v[0].get('Product_name'),
            'Quantity': v[0].get('Quantity'),
            'Description': v[0].get('Description'),
            'ProductId': v[0].get('ProductId'),
            'Price': v[0].get('Price'),
            'image': v[0].get('image'),
            'email':email
        }
        print("product detal :",product_details)
        cart_db.insert_one(product_details) 
        return redirect(product,productId)

        # return render(request,"addcartpage.html", {"b":v,'ob':userDetails[0]})
    else:
        return render(request,"error.html")

# Cart Page 
def cartPage(req):
    email = req.session.get('email')
    print("Current",email)
    userDetails =list(user.find({'email':email}))
    print(userDetails[0])
    if req.method == 'POST':
        last_priceoo = req.POST.get('lastPrice')
        print(last_priceoo)
        v=list(cart_db.find({"email":email}))
        orders.insert_many(v)
        cart_db.delete_many({"email":email})
        return render(req,"success.html",{"ob":userDetails[0],"price":last_priceoo})
    # print(email)
    
    # Page Render
    if email != None:
        userDetails =list(user.find({'email':email}))
        last_priceoo = req.POST.get('lastPrice')
        print(last_priceoo)
        v =[]
        v=list(cart_db.find({"email":email}))
        print(v)
        
        if v!= []:
            fs = gridfs.GridFS(dbb)
            count=0
            for product in v: 
                count+=1
                # print("product Details : ",product)
                if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                    try:
                        f1 = fs.get(product['image'])  # Get the image file from GridFS
                        img_data = f1.read()  # Read the image data
                        product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                    except Exception as e:
                        print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                        product['image_data'] = None  # Handle missing or invalid images
            # v[0]["email"]=email
            # print(v)
            # print(v[0]['Product_name'],len(v))
            # v[0].update({'email':email})
            # print(v)
            print(len(v))
            Total = 0;final_price=0
            for i in range(len(v)):
                Total += int(v[i].get("Price"))
                gst_amount = Total * (18 / 100)    #1500
                final_price = Total + gst_amount
                print(Total,final_price)
            return render(req,"addcartpage.html",{"b" : v,"oblen":len(v),"total":Total,"finalPrice":final_price,"ob":userDetails[0]})
        else:
            return render(req,"cart(empty).html")
    else:
        return render(req,"error.html")
    # return render(req,"addcartpage.html")

def buy(req,productId):
    # print(req.POST['lastPrice'])
    email = req.session.get('email')
    if req.method == 'POST':
        userDetails =list(user.find({'email':email}))
        last_priceoo = req.POST.get('lastPrice')
        print(last_priceoo)
        v =[]
        v=list(products.find({"ProductId":productId}))
        # print(v)
        fs = gridfs.GridFS(dbb)
        for product in v: 
            # print("product Details : ",product)
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        # print(len(v))
        product_details = {
            'Product_name': v[0].get('Product_name'),
            'Quantity': v[0].get('Quantity'),
            'Description': v[0].get('Description'),
            'ProductId': v[0].get('ProductId'),
            'Price': req.POST['lastPrice'],
            'image': v[0].get('image'),
            'email':email
        }
        print("product detal :",product_details)
        orders.insert_one(product_details) 
        return render(req,"success.html",{"b":v[0],"ob":userDetails[0],"price":last_priceoo})
    # print(email)
    print(productId)
    # Page Render
    if email != None:
        userDetails =list(user.find({'email':email}))
        v =[]
        v=list(products.find({"ProductId":productId}))
        # print(v)
        fs = gridfs.GridFS(dbb)
        for product in v: 
            # print("product Details : ",product)
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        # print(len(v))
        Total = 0
        for i in range(len(v)):
            Total += int(v[i].get("Price"))
            gst_amount = Total * (18 / 100)    #1500
            final_price = Total + gst_amount
            # print(Total,final_price)
    
        return render(req,"buy.html",{"ob" : v,"oblen":len(v),"total":Total,"finalPrice":final_price, "email":userDetails[0],"priceDetails":v[0]})
    else:
        return render(req,"error.html") 

def home(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        wish_flag = []
        wish_flag =list(wishlist.find({'email':email}))
        print(wish_flag)
        for i in wish_flag:
            print(i.get('flag'))

        v=[]
        # seller_email = req.session.get('seller_email', None)
        # v=list(photo.find({'email':seller_email}))
        v=list(products.find({}))
        fs = gridfs.GridFS(dbb)
        for product in v: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "main.html",{'b':v ,'ob':userDetails[0],'wish_flag':wish_flag })
    else:
        v=[]
        # seller_email = req.session.get('seller_email', None)
        # v=list(photo.find({'email':seller_email}))
        v=list(products.find({}))
        fs = gridfs.GridFS(dbb)
        for product in v: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "main.html",{'b':v})
# myOrders Page
def myorders(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v =[]
        v=list(orders.find({"email":email}))
        if v!= []:
            fs = gridfs.GridFS(dbb)
            for product in v: 
                if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                    try:
                        f1 = fs.get(product['image'])  # Get the image file from GridFS
                        img_data = f1.read()  # Read the image data
                        product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                    except Exception as e:
                        print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                        product['image_data'] = None  # Handle missing or invalid images
            return render(req,"my_order_copy.html",{"b":v,'ob':userDetails[0]})
        else:
            return render(req,"order(empty).html")
    
    else:
        return render(req,"error.html")
#placeOrder functno
def placeorder(req,buyProduct): 
    print(buyProduct)
    # if req.method == 'POST':
    # last_priceoo = req.POST.get('lastPrice')
    # print(last_priceoo)
    email = req.session.get('email')
    print(email)
    if email != None:
        userDetails =list(user.find({'email':email}))
        v =[]
        v=list(products.find({"ProductId":buyProduct}))
        fs = gridfs.GridFS(dbb)
        for product in v: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        # updatePrice={}
        # updatePrice["lastPrice"] = req.POST["lastPrice"]
        product_details = {
            'Product_name': v[0].get('Product_name'),
            'Quantity': v[0].get('Quantity'),
            'Description': v[0].get('Description'),
            'ProductId': v[0].get('ProductId'),
            'Price': v[0].get('Price'),
            'image': v[0].get('image'),
            'email':email
        }
        orders.insert_one(product_details) 
        return render(req,"success.html",{"ob":v,"email":userDetails[0]})
    else:
        return render(req,"error.html")
#Wish Page
def wish(req):
    email = req.session.get('email')

    if email != None:
        userDetails =list(user.find({'email':email}))
        v =[]
        v=list(wishlist.find({"email":email}))
        if v!= []:
            fs = gridfs.GridFS(dbb)
            for product in v: 
                if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                    try:
                        f1 = fs.get(product['image'])  # Get the image file from GridFS
                        img_data = f1.read()  # Read the image data
                        product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                    except Exception as e:
                        print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                        product['image_data'] = None  # Handle missing or invalid images
            return render(req,"wishlist.html",{"b":v,'ob':userDetails[0]})
        else:
            return render(req,"wish(empty).html")
    else:
        return render(req,"error.html") 

#error page to navigate home page
def error(req):
    return redirect(home) 
# Logout Funciton
def log(req):
    req.session.flush()
    return redirect(home)

def categorymob(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Mobile"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Mobile"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})

def categorylap(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"laptop"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Laptops"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})


def categoryele(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Electronics"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Electronics"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})
   
def categoryhome(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Home Appliance"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Home Appliance"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})


def categoryfas(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Fashion"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Fashion"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})

def categorygro(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Grocery"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Grocery"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})
   
def categoryfur(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Furniture"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Furniture"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "category.html", {'b':v})
   
def categorybea(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Beauty&personalcare"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Beauty&personalcare"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images

        return render(req, "category.html", {'b':v})
   
def categorybab(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))  
        v=[]
        v = list(products.find({'categories':"Baby & Toys"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Baby & Toys"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "category.html", {'b':v})

def categoryspo(req):
    email = req.session.get('email')
    if email != None:
        userDetails =list(user.find({'email':email}))
        v=[]
        v = list(products.find({'categories':"Sports"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "category.html", {'b':v,'ob':userDetails[0]})
    else:
        v=[]
        v = list(products.find({'categories':"Sports"}))  # Filter products by 'furniture' category
        fs = gridfs.GridFS(dbb)
        
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        return render(req, "category.html", {'b':v,})
def add_whish(req, productId):
    email = req.session.get('email')
    print(email)
    if email != None:
        userDetails =list(user.find({'email':email}))
        v =[]
        v=list(products.find({"ProductId":productId}))
        fs = gridfs.GridFS(dbb)
        for product in v: 
            if 'image' in product:  # Ensure 'image' key exists in the product dictionary
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                    product['image_data'] = None  # Handle missing or invalid images
        # updatePrice={}
        # updatePrice["lastPrice"] = req.POST["lastPrice"]
        product_details = {
            'Product_name': v[0].get('Product_name'),
            'Quantity': v[0].get('Quantity'),
            'Description': v[0].get('Description'),
            'ProductId': v[0].get('ProductId'),
            'Price': v[0].get('Price'),
            'image': v[0].get('image'),
            'email':email,
            'flag':'true'
        }
        wishlist.insert_one(product_details) 
        return redirect(home)
    else:
        return render(req,"error.html")

def remove_whish(req, productId):
    email = req.session.get('email')
    wishlist.delete_one({'ProductId':productId})
    return redirect(home)
def remove_whishlist(req, productId):
    email = req.session.get('email')
    print(productId)
    wishlist.delete_one({'ProductId':productId})
    return redirect(wish)
def remove_cart(req, productId):
    email = req.session.get('email')
    print(productId)
    cart_db.delete_one({'ProductId':productId})
    return redirect(cartPage)


import logging

logger = logging.getLogger(__name__)

def search1(req):
    """
    Handles product search requests.
    Retrieves relevant product data from the database and passes it to the template.
    """
    email = req.session.get('email')
    userDetails = list(user.find({'email': email}))

    if req.method == 'POST':
        search_query = req.POST.get('search', '').strip()
        if not search_query:
            return render(req, "search.html", {'error': 'Search query cannot be empty.'})

        fs = gridfs.GridFS(dbb)
        try:
            products_found = list(products.find({"Product_name": {"$regex": search_query, "$options": "i"}}))
            suggested_products = list(products.find().limit(5))  # Fetch 5 random suggestions

            for product in products_found + suggested_products:
                if 'image' in product:
                    try:
                        f1 = fs.get(product['image'])
                        img_data = f1.read()
                        product['image_data'] = base64.b64encode(img_data).decode('utf-8')
                    except Exception as e:
                        logger.error(f"Error fetching image for product {product.get('_id')}: {e}")
                        product['image_data'] = None

            if products_found:
                return render(req, "search.html", {'ob': products_found, 'ob1': len(products_found), 'user_detail': userDetails[0] if userDetails else None})
            else:
                return render(req, "search.html", {'error': 'No products found.', 'suggested_products': suggested_products})
        except Exception as e:
            logger.error(f"Error processing search: {e}")
            return render(req, "search.html", {'error': 'An error occurred while processing your search.'})

    return redirect('home')

def cad_brand(request):
    v = []
    brands = set()  # To store unique brands
    

    # Fetch all products
    v = list(products.find())
    
    # Extract unique brands
    brands = set(product.get('brand', '') for product in v if 'brand' in product)
    
    # Get the selected brand from the request
    selected_brand = request.GET.get('brand', '')

    if selected_brand:
        # Filter products based on the selected brand
        v = list(filter(lambda product: product.get('brand') == selected_brand, v))

    # Fetch images from GridFS
    fs = gridfs.GridFS(dbb)
    for product in v:
        if 'image' in product:
            try:
                f1 = fs.get(product['image'])
                img_data = f1.read()
                product['image_data'] = base64.b64encode(img_data).decode('utf-8')
            except Exception as e:
                print(f"Error fetching image for product {product.get('_id')}: {e}")
                product['image_data'] = None

    return render(request, "search.html", {'ob2': v, 'brands': brands, 'selected_brand': selected_brand})


def cad_brand1(request):
    v=[]
    #    def cad(request):
    # Fetch products in the "furniture" category
    v = list(products.find({'brand': 'Poco'}))  # Filter products by 'furniture' category
    fs = gridfs.GridFS(dbb)
    
    for product in v:
        if 'image' in product:  # Ensure 'image' key exists in the product dictionary
            try:
                f1 = fs.get(product['image'])  # Get the image file from GridFS
                img_data = f1.read()  # Read the image data
                product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
            except Exception as e:
                print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                product['image_data'] = None  # Handle missing or invalid images
    print(v)
    return render(request, "search.html", {'ob':v})

def cad_brand2(request):
    v=[]
    #    def cad(request):
    # Fetch products in the "furniture" category
    v = list(products.find({'brand': 'Apple'}))  # Filter products by 'furniture' category
    fs = gridfs.GridFS(dbb)
    
    for product in v:
        if 'image' in product:  # Ensure 'image' key exists in the product dictionary
            try:
                f1 = fs.get(product['image'])  # Get the image file from GridFS
                img_data = f1.read()  # Read the image data
                product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
            except Exception as e:
                print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log any error
                product['image_data'] = None  # Handle missing or invalid images
    print(v)
    return render(request, "search.html", {'ob':v})


def color1(request):
    """
    Fetch and display products filtered by the color 'black',
    along with user details for the session email.
    """
    try:
        v = []  # Initialize the product list
        email = request.session.get('email')  # Get email from session

        # Fetch user details
        userDetails = list(user.find({'email': email}))
        user_detail = userDetails[0] if userDetails else None  # Get the first user detail or None

        # Fetch products filtered by color
        v = list(products.find({'color': 'black'}))  # Filter products by color
        fs = gridfs.GridFS(dbb)

        # Process product images
        for product in v:
            if 'image' in product:  # Ensure 'image' key exists
                try:
                    f1 = fs.get(product['image'])  # Get the image file from GridFS
                    img_data = f1.read()  # Read the image data
                    product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
                except Exception as e:
                    print(f"Error fetching image for product {product.get('_id')}: {e}")
                    product['image_data'] = None  # Handle missing or invalid images

        # Render the response
        return render(request, "search.html", {'ob': v, 'ob2': user_detail})

    except Exception as e:
        print(f"Error in color1 function: {e}")
        return render(request, "search.html", {'error': 'An error occurred while processing your request.'})

def fetch_user_detail(email):
    """Helper function to fetch user details."""
    userDetails = list(user.find({'email': email}))
    return userDetails[0] if userDetails else None

def process_products(product_list, fs):
    """Helper function to process products and fetch images."""
    for product in product_list:
        if 'image' in product:
            try:
                f1 = fs.get(product['image'])  # Get the image file from GridFS
                img_data = f1.read()  # Read the image data
                product['image_data'] = base64.b64encode(img_data).decode('utf-8')  # Encode to base64
            except Exception as e:
                print(f"Error fetching image for product {product.get('_id')}: {e}")  # Log error
                product['image_data'] = None  # Handle missing or invalid images
    return product_list

def color2(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find({'color': 'red'}))  # Filter products by 'red' color
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})

def color3(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find({'color': {'$ne': 'red'}}))  # Products not 'red'
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})

def ascen(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find().sort('Price', 1))  # Sort by ascending price
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})

def descn(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find().sort('Price', -1))  # Sort by descending price
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})

def low(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find().sort('Product_name', 1))  # Sort alphabetically
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})

def high(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find().sort('Product_name', -1))  # Reverse alphabetical
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})

def newest(request):
    email = request.session.get('email')
    user_detail = fetch_user_detail(email)
    v = list(products.find().sort('_id', -1))  # Most recently added products
    fs = gridfs.GridFS(dbb)
    v = process_products(v, fs)
    return render(request, "search.html", {'ob': v, 'ob2': user_detail})
