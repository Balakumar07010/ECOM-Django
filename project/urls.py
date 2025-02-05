"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('userLogin',views.userLogin, name="userLogin"),
    path('userReg',views.userReg,name="userReg"),
    path('sellerLogin',views.sellerLogin, name="sellerLogin"),
    path('sellerRegister',views.sellerRegister,name="sellerRegister"),
    path('dashboard',views.dashboard),
    path('profile',views.sellerProfile,name="seller_profile"), #view the profile Page
    path('addProducts',views.addProducts,name="add_product"),
    path('myProduct',views.myProducts,name="my_product"),
    path('salesReport',views.salesReport,name="Sales_Report"),
    path('updateprofile',views.sellerProfile,name="updatesellerprofile"), #update a product
    path('user_Profile',views.user_profile,name="user_Profile"), #update a product
    path('homePage',views.homePage,name="homePage"), #Return Home Page
    path('updateitem',views.updateitem,name="updateitem"),
    path('deleteitem/<str:ProductId>',views.deleteitem,name="deleteitem"),
    path('product/<str:productId>/',views.product,name="product",),
    path('cart/<str:productId>/',views.cart,name="cart"),
    path('cart',views.cartPage,name="cartPage"),
    path('buy/<str:productId>/',views.buy,name="buy"),
    path('home',views.error,name="error"),
    path('placeorder/<str:buyProduct>/',views.placeorder,name="placeorder"),
    path('whishlist',views.wish,name="whishlist"),

    path('myOrders',views.myorders,name="myOrders"),
    path('logout',views.log,name="logout"),
    path('categorymob',views.categorymob,name="categorymob"),
    path('categorylap',views.categorylap,name="categorylap"),
    path('categoryele',views.categoryele,name="categoryele"),
    path('categoryhome',views.categoryhome,name="categoryhome1"),
    path('categoryfas',views.categoryfas,name="categoryfas"),
    path('categorygro',views.categorygro,name="categorygro"),
    path('categoryfur',views.categoryfur,name="categoryfur"),
    path('categorybea',views.categorybea,name="categorybea"),
    path('categorybab',views.categorybab,name="categorybab"),
    path('categoryspo',views.categoryspo,name="categoryspo"),

    path('add_whish/<str:productId>/',views.add_whish,name="add_whish"),
    path('remove_whish/<str:productId>/',views.remove_whish,name="remove_whish"),
    path('remove_cart/<str:productId>/',views.remove_cart,name="remove_cart"),
    path('remove_whishlist/<str:productId>/',views.remove_whishlist,name="remove_whishlist"),
    path('search21',views.search1,name="search"),
    path('search1',views.cad_brand,name="search1"),
    path('search2',views.cad_brand1,name="search2"),
    path('search3',views.cad_brand2,name="search3"),
    path('color',views.color1,name="color1"),
    path('color1',views.color2,name="color2"),
    path('color2',views.color3,name="color3"),
    path('lowtohigh',views.ascen,name='lowtohigh'),
    path('hightolow',views.descn,name='hightolow'),
    path('atoz',views.low,name='atoz'),
    path('ztoa',views.high,name='ztoa'),
    path('newest',views.newest,name='newest'),

]
