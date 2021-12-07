(function () {
    LiveConversion();
    comprarBitcoin();
    $(".box.single a").on("click", async function() {
        let lempiras = $(this).find('.precio').val();
        let result = await calcularConversion("BTC");
        let btc = (parseFloat(lempiras) / result).toFixed(8);
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);
        $("#id_amount_field").prop('readonly', 'readonly');
        $("#id_lempiras_field").prop('readonly', 'readonly');
    });

    // Validate a credit card number
    //$.payform.validateCardNumber('4242 4242 4242 4242'); //=> true

    // Get card type from number
    //$.payform.parseCardType('4242 4242 4242 4242'); //=> 'visa'
})();

function calcularConversion(criptomoneda) {
    return new Promise(resolve => {
        var oReq = new XMLHttpRequest();
        oReq.responseType = "json";
        oReq.open("GET", "https://bitpay.com/api/rates/" + criptomoneda, true);
        oReq.send(null);

        oReq.onreadystatechange = function (aEvt) {
            if (oReq.readyState == 4) {
                if (oReq.status == 200) {
                    let result = oReq.response[68].rate;
                    result += 0.1 * result;
                    resolve(result);
                }
            }
        };
    });
}

function LiveConversion() {
    document.getElementById('textInput').oninput = async function() {
        let result = await calcularConversion("BTC");
        document.getElementById("textInput2").value = result * parseFloat(document.getElementById('textInput').value);
    };

    document.getElementById('textInput2').oninput = async function() {
        let result = await calcularConversion("BTC");
        document.getElementById("textInput").value = (parseFloat(document.getElementById('textInput2').value) / result).toFixed(8);
    };
}

function comprarBitcoin() {
    $("#btncomprar").on("click", function () {
        let btc = $("#textInput").val();
        let lempiras = $("#textInput2").val();
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);
        $("#id_amount_field").prop('readonly', 'readonly');
        $("#id_lempiras_field").prop('readonly', 'readonly');
    });
}



