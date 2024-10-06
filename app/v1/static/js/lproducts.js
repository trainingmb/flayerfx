
var count = 1;
async function getContent(url, data)
{
    let response = await fetch(url, {
        method: "PUT",
        headers: {
            "Content-type": "application/json"
        },
        data:data
    });
    if(response.ok)
    {
        console.log("Got it");
        let jso = await response.json();
        console.log(jso);
        renderproducts(jso);
    }
    else
    {
        console.log("Failed Retry");
    }
}
function returnproducttag(product, link)
{
    var wrapper = document.createElement('li');
    var atag = document.createElement('a');

    atag.innerText = product.name;
    atag.classList.add("link");
    atag.setAttribute('href', link.replace('product_id', product.id));
    wrapper.appendChild(atag.cloneNode(true));

    if (product.price_count == 0){
        wrapper.innerHTML += " ()" + product.price_count;
    }
    else
    {
        wrapper.innerHTML += " (" + product.latest_price.amount + ")" + product.price_count;
    }
    return wrapper;
}

function renderproducts(products)
{
    var store_id = document.getElementById("store_id");
    var adddiv = document.getElementById("static_prod_in_store");
    var deflink = document.getElementById("product_in_store_url").innerText;
    var fulllist = document.createElement('ul');
    adddiv.innerHTML = "";
    for (var i = products.length - 1; i >= 0; i--) {
        fulllist.appendChild(returnproducttag(products[i], deflink).cloneNode(true));
    }
    adddiv.appendChild(fulllist.cloneNode(true));
}
async function loadContent()
{
    data = {};
    data.page = count;
    console.log(data);
        await  getContent(document.getElementById("api_products_in_store_url").innerText, data);
        count++;
}