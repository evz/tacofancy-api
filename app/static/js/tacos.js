(function(){
    $(document).ready(function(){
        $.when(get_tacos()).then(
            function(taco){
                var main_title = taco.base_layer.name + ' <strong>with</strong> ';
                main_title += taco.mixin.name + ', <strong>garnished with</strong> ';
                main_title += taco.condiment.name + ' <strong>topped off with</strong> ';
                main_title += taco.seasoning.name + '<strong> and wrapped in delicious</strong> ';
                main_title += taco.shell.name;
                document.title = taco.base_layer.name + ' | ' + taco.mixin.name + ' | ' + taco.condiment.name + ' | ' + taco.seasoning.name + ' | ' + + taco.shell.name;
                $('#taco-content').append('<h1 class="light">' + main_title + '</h1>');
                var permalink = '/' + taco.base_layer.slug + '/';
                permalink += taco.mixin.slug + '/';
                permalink += taco.condiment.slug + '/';
                permalink += taco.seasoning.slug + '/';
                permalink += taco.shell.slug + '/';
                $('#taco-content').append('<a href="' + permalink + '"><h5 class="light">Permalink to this taco</a></h5><hr/>')
                var renderer = new EJS({url: '/static/js/views/taco.ejs'});
                $('#taco-content').append(renderer.render(taco));
            }
        )
    });
    function get_tacos(){
        return $.ajax({
            url: '/random/',
            type: 'GET',
            dataType: 'json'
        })
    }
})()
