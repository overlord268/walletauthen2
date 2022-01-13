let secs = 60;
let countDown = secs;

var timer = new Timer(async function() {
    document.getElementById("counter").innerHTML = "Válido durante " + countDown + "s ";
    countDown -= 1;

    if (countDown == 0) {
        countDown = secs;
        let result = await calcularConversion();
        let lempiras = $("#id_lempiras_field").val();
        let btc = (parseFloat(lempiras) / result).toFixed(8);
        $("#id_amount_field").val(btc);
    }
}, 1000);

(function () {
    LiveConversion();
    comprarBitcoin();

    timer.stop();

    $(".box.single a").on("click", async function() {
        let lempiras = $(this).find('.precio').val();
        let result = await calcularConversion();
        let btc = (parseFloat(lempiras) / result).toFixed(8);
        $("#id_amount_field").val(btc);
        $("#id_lempiras_field").val(lempiras);

        timer.reset(1000);
    });
})();

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
        
        timer.reset(1000);
    });
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

function Timer(fn, t) {
    var timerObj = setInterval(fn, t);

    this.stop = function() {
        if (timerObj) {
            clearInterval(timerObj);
            timerObj = null;
        }
        return this;
    }
    this.start = function() {
        if (!timerObj) {
            this.stop();
            timerObj = setInterval(fn, t);
        }
        return this;
    }
    this.reset = function(newT = t) {
        t = newT;
        countDown = secs;
        return this.stop().start();
    }
}
