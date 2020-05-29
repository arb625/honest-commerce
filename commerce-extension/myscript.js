
window.onload = function() {
    setTimeout(function() {
        console.log("started")

        if (document.title.indexOf("Sell on eBay") != -1) {
            console.log("inside")

            function sendListPostRequest() {

                var physical = ["PURELL 9651-24 Advanced Instant Hand Sanitizer - 4oz", "Mask"]

                var upc = document.getElementById("wc0-w0-LIST_PAGE_WRAPPER__-OCS_DESCRIBE_SECTION__-ATTRIBUTES__-ATTRIBUTES_GH__-ATTRIBUTES_DIY_VIEW__-RECOMMENDED_GROUP__-recommendedAttributesMoreOptions__-ADDITIONAL_GROUP__-additionalAttributesMoreOptions__-MORE_ADDITIONAL_ATTRIBUTE_GRID__-restOfAdditionalAttrList.3__-valueSelect-w1").innerText
                var itemName = document.getElementById("wc0-w0-LIST_PAGE_WRAPPER__-OCS_DESCRIBE_SECTION__-TITLE__-titleField__-textbox").innerText
                var category = physical.includes(itemName) ? "physical" : "digital"
                var price = Number(document.getElementById("wc0-w0-LIST_PAGE_WRAPPER__-PRICE_VIEW__-PRICE_DETAIL_VIEW__-w1-binDiyPriceGroup__-binDiyPriceGroupNew__-binPrice__-textbox").value)
                var quantity = Number(document.getElementById("wc0-w0-LIST_PAGE_WRAPPER__-PRICE_VIEW__-PRICE_DETAIL_VIEW__-priceMoreOptions__-PRICE_MORE_OPTIONS_GROUP__-quantitySelection__-quantity__-textbox").value)
                var sellerId = document.getElementById("wc0-w0-LIST_PAGE_WRAPPER__-LISTING_PREFERENCES_OVERLAY__-w0-paypalEmailAddress__-valueSelect-w2").innerText

                if (category === "digital") {
                    body = {
                        "category": category,
                        "ticketId": upc,
                        "name": name,
                        "price": price,
                        "sellerId": sellerId,
                        "isVerifiedSeller": false,
                    }
                } else if (category === "physical") {
                    body = {
                        "category": category,
                        "sku": upc,
                        "name": name,
                        "price": price,
                        "quantity": quantity,
                        "sellerId": sellerId,
                        "isVerifiedSeller": false,
                    }
                }

                sendPostRequest("/list", body)


            }

            const sendPostRequest = async (route, body) => {
                const response = await fetch("http://localhost:5000/" + route, {
                    method: "POST",
                    body: body,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const myJson = await response.json(); //extract JSON from the http response
                // do something with myJson
            }

            const sendGetRequest = async (route) => {
                const response = await fetch("http://localhost:5000/" + route);
                const myJson = await response.json(); //extract JSON from the http response
                // do something with myJson
            }

            var listButton = document.getElementById("wc0-w0-LIST_PAGE_WRAPPER__-CTA__-CTA_VIEW__-listItCallToAction__")
            
            var newButton = document.createElement("BUTTON")
            newButton.id = "new_button"
            newButton.style.height = "40px"
            newButton.style.width = "450px"
            newButton.style.backgroundColor = "orange"
            newButton.innerText = "List!"
            newButton.addEventListener("click", sendListPostRequest)
            console.log("added listener")
            
            listButton.parentNode.replaceChild(newButton, listButton);
            console.log("replaced")
            
        }
    }, 5000)

}