
let hoy = new Date();
var Selfuser = "";
document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', () => {

        socket.on('message', function (msg) { //la conexion del cliente a servidor.
            var hour = hoy.getHours() + ':' + hoy.getMinutes();
            if (localStorage.getItem("username") == $('#username').val()) {
                $('#texto-msj').append('<li style="list-style:none; widht:100%; margin:5px; height:auto;"><div style="float:right; max-width:95%; min-width:15%;  padding-left:5px; padding-right:5px; font-family: Arial, Helvetica, sans-serif; background:#ffff;  height:auto; border-radius:5px;">' + '<div style="color:green;">' +"You"+ '</div> <div style="margin-right:5px;">' + msg + '</div><div style="float:right; color:gray; font-size:10px; margin-top:5px; margin-right:5px;">'+hour+'</div></div></li>'); // insertamos el contenido de a la lista, es decir el texto-msj.
            } else {
                $('#texto-msj').append('<li style="list-style:none; margin:5px; widht:100%; height:auto;"><div style="float:left; max-width:95%; min-width:15%; padding-left:5px; padding-right:5px; font-family: Arial, Helvetica, sans-serif; background:#ffff; height:auto; border-radius:5px;">' + '<div style="color:blue;">' + localStorage.getItem("username") + '</div> <div style="margin-right:5px;">' + msg + '</div><div style="float:right; color:gray; font-size:10px; margin-top:5px; margin-right:5px;">'+hour+'</div></div></li>'); // insertamos el contenido de a la lista, es decir el texto-msj.
            }
        });

        $('#Enviar').on('click', function () { //nuestro boton tendra la funcion al momento de clikear de mandar ese contenido a texto-msj
            socket.send($('#mi-msj').val());
            $('#mi-msj').val('');
        });

        $('#Salir').on('click', function (){
            socket.emit('left', {}, function () {
                socket.disconnect();
                // go back to the login page
                
            });
            cerrarMessages();
        });

       
        

    });

});

function setUsername(user) {
   localStorage.setItem("username",user);
    var hour = hoy.getHours() + ':' + hoy.getMinutes();
    var newMessage = {
        username:user,
        msg: $('#mi-msj').val(),
        group: $('#group-name').val(),
        hour: hour
    };

    MsgList.push(newMessage);
    setMessage(MsgList);
    
}

function getMessage(){
    var storedList = localStorage.getItem('MessageList');
    if(storedList == null){
        MsgList = [];

    }else{
        MsgList = JSON.parse(storedList);
    }    
    return MsgList;
}

function setMessage(newMessage){
    localStorage.setItem('MessageList', JSON.stringify(newMessage));
}

function MostrarChat(name, img, group) {
    
    $("#Username-message").text(group);
    $("#group-name").val(group);
    $("#img-message").attr("src", img);
    var list = getMessage();
    for(var i = 0; i < list.length; i++){
        console.log(list[i].username+"-"+list[i].group+"-"+list[i].msg);
        
        if (list[i].username == name && list[i].group == group) {
            $('#texto-msj').append('<li style="list-style:none; widht:100%; margin:5px; height:auto;"><div style="float:right; max-width:95%; min-width:15%;  padding-left:5px; padding-right:5px; font-family: Arial, Helvetica, sans-serif; background:#ffff;  height:auto; border-radius:5px;">' + '<div style="color:green;">' +"You"+ '</div> <div style="margin-right:5px;">' + list[i].msg + '</div><div style="float:right; color:gray; font-size:10px; margin-top:5px; margin-right:5px;">'+list[i].hour+'</div></div></li>'); // insertamos el contenido de a la lista, es decir el texto-msj.
    
        } else if(list[i].username != name && list[i].group == group){
            
            $('#texto-msj').append('<li style="list-style:none; margin:5px; widht:100%; height:auto;"><div style="float:left; max-width:95%; min-width:15%; padding-left:5px; padding-right:5px; font-family: Arial, Helvetica, sans-serif; background:#ffff; height:auto; border-radius:5px;">' + '<div style="color:blue;">' + list[i].username + '</div> <div style="margin-right:5px;">' + list[i].msg + '</div><div style="float:right; color:gray; font-size:10px; margin-top:5px; margin-right:5px;">'+list[i].hour+'</div></div></li>'); // insertamos el contenido de a la lista, es decir el texto-msj.
        }
       
    }
    $("#message").children().show();

}

window.onpageshow = function () {
    //localStorage.removeItem('MessageList');
    cerrarMessages();
}

function cerrarMessages(){
    var ancho = window.innerWidth;

    if (ancho < 600) {
        $("#message").hide();
    } else {
        $("#message").children().hide();
    }

    $('#texto-msj').children().hide();
}
