(function () {
    LiveConversion();
    comprarBitcoin();
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
                    result += result * 0.1;
                    resolve(result);
                }
            }
        };
    });
}

function calculo(valor) {
    let resultado = valor + valor * 0.1;
    resultado = resultado.toLocaleString("de-DE", {
        style: "currency",
        currency: "HNL",
        minimumFractionDigits: 4,
    });
    console.log("Resultado", result);
    return resultado;
}

function LiveConversion() {
    $("#textInput").on("change", async function () {
        let result = await calcularConversion("BTC");
        document.getElementById("textInput2").value = result * parseFloat($(this).val());
    });

    $("#textInput2").on("change", async function () {
        let result = await calcularConversion("BTC");
        document.getElementById("textInput").value = parseFloat($(this).val()) / result;
    });
}

function comprarBitcoin() {
    $("#btncomprar").on("click", function () {
        let btc = document.getElementById("textInput").value;
        console.log(btc);
        document.getElementById("amount").value = btc;
    });


}



