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
            console.log('Entered Plus')
            window.location.href = '/wishlist/?added_to_wishlist=true';
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
            console.log('Entered Minus')
            window.location.href = '/wishlist/?removed_from_wishlist=true';

        }
    })
})
})