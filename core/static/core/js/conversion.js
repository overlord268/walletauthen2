(function () {
    LiveConversion();
    comprarBitcoin();
    $(".box.single a").on("click", async function() {
        let lempiras = $(this).find('.precio').val();
        let result = await calcularConversion();
        let btc = (parseFloat(lempiras) / result).toFixed(8);
        $("#id_cambio_btc_lempiras").val(result);
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);
    });
})();

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
        let cambio = $("#textInput3").val();
        $("#id_cambio_btc_lempiras").val(cambio);
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);
    });
}



