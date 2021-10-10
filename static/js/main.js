
function MostrarChat(name,img){
        $("#Username-message").text(name);           
        $("#img-message").attr("src",img);
        $("#message").children().show();
}
window.onpageshow = function () {

        var ancho = window.innerWidth;
        
    if(ancho < 600){
        $("#message").hide();    
    }else{
        $("#message").children().hide(); 
    }    
      
}
