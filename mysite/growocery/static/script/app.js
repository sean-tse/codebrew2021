function volunteerBuyerCallback() {
    const overlay = document.getElementById("overlay-bg")
    overlay.style.display = "block"
}

function volunteerBuyerCancelCallback() {
    const overlay = document.getElementById("overlay-bg")
    overlay.style.display = "none"
}

function confirmOrderCallback() {
    var invoiceGenerated = '{{ myorder.invoiceGenerated }}'
    const confirmPayButton = document.getElementById("confirm-pay-button")
    console.log(invoiceGenerated)
    if (invoiceGenerated == true) {
        confirmPayButton.disabled = true
    } else {
        confirmPayButton.disabled = false
    }
}