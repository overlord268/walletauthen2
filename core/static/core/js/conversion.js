(function () {
    LiveConversion();
    comprarBitcoin();
    $(".box.single a").on("click", async function() {
        let lempiras = $(this).find('.precio').val();
        let result = await calcularConversion();
        let btc = (parseFloat(lempiras) / result).toFixed(8);
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);

        counter(lempiras, 60);
    });
})();

function counter(lempiras, secs) {
    var countDown = secs;

    setInterval(async function() {
        document.getElementById("counter").innerHTML = "Válido durante " + countDown + "s ";
        countDown -= 1;
    
        if (countDown == 0) {
            let result = await calcularConversion();
            let btc = (parseFloat(lempiras) / result).toFixed(8);
            $("#id_amount_field").val(btc);
            countDown = secs;
        }
    }, 1000);
}

function calcularConversion() {
    return new Promise(resolve => {
        $.ajax({
            type: "GET",
            url: "/conversion/",
            success: function(data){
                console.log("success");
                resolve(data.conversion);
            },
            failure: function(data){
                console.log("failure");
            },
        });
    });
}

function LiveConversion() {
    document.getElementById('textInput').oninput = async function() {
        let result = await calcularConversion();
        document.getElementById("textInput3").value = result;
        document.getElementById("textInput2").value = result * parseFloat(document.getElementById('textInput').value);
    };

    document.getElementById('textInput2').oninput = async function() {
        let result = await calcularConversion();
        document.getElementById("textInput3").value = result;
        document.getElementById("textInput").value = (parseFloat(document.getElementById('textInput2').value) / result).toFixed(8);
    };
}

function comprarBitcoin() {
    $("#btncomprar").on("click", function () {
        let btc = $("#textInput").val();
        let lempiras = $("#textInput2").val();
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);
        
        counter(lempiras, 60);
    });
}



