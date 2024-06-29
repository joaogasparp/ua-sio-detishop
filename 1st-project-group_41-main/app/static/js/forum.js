



$(function() {
    getposts = function() 
    {
        console.log("lol");
        $.getJSON('get_posts', function(data) 
        {
            console.log(data);
            html = ""
            //render_items(data);
            $.each( data, function( index, item ) 
            {
                html += `            
                    <div class="card mt-3">
                        <div class="card-body">
                            <h5 class="card-title">Título: ${ item.title }</h5>
                            <p class="card-text">Mensagem: ${ item.message }</p>
                        </div>
                    </div>
                    `;

                
            });
            console.log(html);

            $('#posts').html(html);
        })
        .done(function() {
        });
    }
    getposts();
    
})