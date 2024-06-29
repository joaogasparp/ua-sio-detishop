

let last_value = $('#amount').val();

function render_items(data) {
    
    let list = $('#item-list');

    list.html('');
    $.each( data.data, function( index, item ) {
        console.log(item);
        let availability = "";
        let html_to_append = "";
        if (item.stock == 0) {
            availability = 
            `
            <i class="fa fa-circle text-danger" aria-hidden="true"></i>
            <span>Sem stock</span>
            `
        } else if (item.stock <= 5) {
            availability = 
            `
            <i class="fa fa-circle text-warning" aria-hidden="true"></i>
            <span>Poucas unidades</span>
            `
        } else {
            availability = 
            `
            <i class="fa fa-circle text-success" aria-hidden="true"></i>
            <span>Disponivel</span>
            `
        }
        
        html_to_append += 
        `
        <div class="col-sm-6 col-lg-4 mb-4" data-aos="fade-up">
            <div class="block-4 text-center border">
                <figure class="block-4-image">
                    <a href="/product/${ item.id }"><img src="images/products/${ item.product_image }" alt="Image placeholder" class="img-fluid"></a>
                </figure>
                <div class="block-4-text p-4">
                    <h3><a href="/product/${ item.id }"> ${item.name}</a></h3>
                    <p class="mb-0">${item.description}</p>
                    <p class="text-primary font-weight-bold">${item.price} €</p>
                    <p class="mb-0 availability-product">
                        ${availability}                        
                    </p>
                </div>
            </div>
        </div>
        `
        list.append(html_to_append);


    });
}

$(function() {
    $('#slider-range').on('slidechange', function() {
        curr_value = $('#amount').val();
        
        if (last_value !== curr_value) {
            last_value = curr_value;
            console.log(curr_value);

            let url = new URL(window.location.href)
            url.searchParams.set('range', curr_value);

            $.get(url, function(data) {
                //render_items(data);
                $("#item-list").html(data);
            })
            .done(function() {
                history.pushState({}, null, url);
            });
            return false;
        }
    });

    $('#show_available, #show_out_of_stock').on('input', function() {
        let show_available = $('#show_available').prop('checked')
        let show_out_of_stock = $('#show_out_of_stock').prop('checked')
        
        let url = new URL(window.location.href)
        url.searchParams.set('show_available', show_available);
        url.searchParams.set('show_out_of_stock', show_out_of_stock);

        $.get(url, function(data) {
            //render_items(data);
            $("#item-list").html(data);
        })
        .done(function() {
            history.pushState({}, null, url);
        });
        return false;
    })

    
});


