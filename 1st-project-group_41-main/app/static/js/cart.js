function alterarTextoECor() {
    var paragraph = document.getElementById("InvalidCoupon");
    paragraph.innerHTML = "Invalid Coupon!";
    paragraph.style.color = "red";
}

var applyCouponButton = document.getElementById("applyCouponButton");
applyCouponButton.addEventListener("click", alterarTextoECor);

function removeFromCart(productId) {
    console.log(productId);
    $.ajax({
        type: "POST",
        url: "/cart",  // Deve corresponder à rota do Flask que trata a remoção do produto
        dataType: 'json',
        data: JSON.stringify( {
            "product_id": productId
        }),
        success: function (response) {
            // Recarregue a página após a remoção bem-sucedida
            //location.reload();
            console.log("lol");      
        },error : function(result){

            console.log("ERRORRRRRRRRRRRRR");     
            console.log(result);
         }
    });
  }