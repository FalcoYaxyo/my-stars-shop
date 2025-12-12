<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Stars va Gift Sotish</title>
</head>
<body>
    <h1>Stars va Gift sotib olish</h1>
    <label for="amount">Miqdor (UZS):</label>
    <input type="number" id="amount" value="100">
    <br><br>
    <button onclick="pay('click')">Click orqali to‘lash</button>
    <button onclick="pay('payme')">Payme orqali to‘lash</button>

    <script>
        function pay(method){
            let amount = document.getElementById('amount').value;
            let order_id = Date.now(); // Unikal order id
            if(method === 'click'){
                window.open(`https://api.click.uz/v2/payment/create?amount=${amount}&order_id=${order_id}`, '_blank');
            } else {
                window.open(`https://checkout.payme.uz/api/checkout/create?amount=${amount}&order_id=${order_id}`, '_blank');
            }
        }
    </script>
</body>
</html>