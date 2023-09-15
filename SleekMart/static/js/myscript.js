$(document).ready(function() {
$('.plus-wishlist').click(function(){
    console.log('Plus Wishlist Button Clicked'); // Add this line
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/plus_wishlist",
        data:{
            prod_id:id
        },
        success:function(data)
        {
            window.location.href = `http://localhost:8000/single_product/${id}`
        }
    })
})

$('.minus-wishlist').click(function(){
    console.log('Minus Wishlist Button Clicked'); 
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minus_wishlist",
        data:{
            prod_id:id
        },
        success:function(data)
        {
            window.location.href = `http://localhost:8000/single_product/${id}`

        }
    })
})
})