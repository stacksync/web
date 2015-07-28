//Globales
var lastSelected = undefined;
var stopAnimation = undefined;

$(document).ready(function()
{
	loadEvents();
    sendPathlist();
});

function loadEvents()
{   	
	$.jGrowl.defaults.closerTemplate = '<div>' + gettext('close') + '</div>';
	function warning() {	
	    var freqSecs = 0.8;
	    stopAnimation = setInterval (RepeatCall, freqSecs*1000 );
	    function RepeatCall() {
	      var inout = (freqSecs*1000)/2;
	      $("#status-files").fadeIn(inout).fadeOut(inout);
	    }
	}
	
	$(function() {	   			
		$('#select_lang').off('change');
		$('#select_lang').change(function() {				
			$("#form_select_lang").submit();			
		});
	});

	$(function() {
		$('#body tr').off('click');
		$('#body tr').click(function(){
            $(this).toggleClass('selected');
			if($(this).hasClass('selected') || $('#body tr.selected').length == 1)
			{		
				lastSelected = this.id;
				if($('#body tr.selected').length > 1)
				{
					$('#compartir, #downloadFile, #mover, #renombrar').hide();
					if($('#tabla_principal').hasClass('col-md-8'))
					{
						$('div.metadataFiles').removeClass('col-md-4').hide();
						$('div.metadataFiles').removeClass('col-md-4').hide();
                        $('#tabla_principal').removeClass('col-md-8');
					}
				}	
				else if($('#body tr.selected').children().hasClass('showContext'))
				{
					lastSelected = $('#body tr.selected').attr('id');
                    $('#downloadFile, #mover, #renombrar, #borrar').show();
					if($('#tabla_principal').hasClass('col-md-8'))
					{
						$('div.metadataFiles').removeClass('col-md-4').hide();
						$('#tabla_metainformacion_' + lastSelected).addClass('col-md-4');
					    $('#tabla_metainformacion_' + lastSelected).show();
					}
				}
				else
				{
                    lastSelected = $('#body tr.selected').attr('id');
					$('#compartir, #mover, #renombrar, #borrar').show();
					if($('#tabla_principal').hasClass('col-md-8'))
					{
						$('div.metadataFiles').removeClass('col-md-4').hide();
						$('#tabla_metainformacion_' + lastSelected).addClass('col-md-4');
					    $('#tabla_metainformacion_' + lastSelected).show();
					}
				}
			}	
			else if(!$('#body tr').hasClass('selected'))
			{				
				$('#botones td.butOptional').hide();
				$('#tabla_principal').removeClass('col-md-8');
				$('div.metadataFiles').removeClass('col-md-4');
				$('div.metadataFiles').hide();
			}				
		});
	});	
	
	//Selector para añadir select con botón derecho
	$(function() {
		$('#body tr').off('mousedown');
		$('#body tr').mousedown(function(event){
			if(event.which === 3)
			{
				$(this).addClass('selected');					
				lastSelected = this.id;				
				if($('#body tr.selected').length > 1)
				{					
					$('#compartir, #downloadFile, #mover, #renombrar').hide();
					if($('#tabla_principal').hasClass('col-md-8'))
					{
						$('div.metadataFiles').removeClass('col-md-4').hide();
						$('#tabla_metainformacion_' + lastSelected).addClass('col-md-4');
					    $('#tabla_metainformacion_' + lastSelected).show();
					}
				}	
				else if($(this).children().hasClass('showContext'))
				{
					$('#downloadFile, #mover, #renombrar, #borrar').show();
					if($('#tabla_principal').hasClass('col-md-8'))
					{
						$('div.metadataFiles').removeClass('col-md-4').hide();
						$('#tabla_metainformacion_' + lastSelected).addClass('col-md-4');
					    $('#tabla_metainformacion_' + lastSelected).show();
					}
				}
				else
				{
					$('#compartir, #mover, #renombrar, #borrar').show();						
					if($('#tabla_principal').hasClass('col-md-8'))
					{
						$('div.metadataFiles').removeClass('col-md-4').hide();
						$('#tabla_metainformacion_' + lastSelected).addClass('col-md-4');
					    $('#tabla_metainformacion_' + lastSelected).show();
					}
				}							
			}
		});
	});		
	
	$(function() {
		$('#borrar').off('click');
		$('#borrar').click(function(){
            var data = [];
            clearInterval(stopAnimation);
            $('#body tr.selected').each(function () {
                data.push(this.id);
            });
            if (data.length === 0) return;
            $('#status-files').removeClass('progress-bar-success').css('width', '100%');
            $('#status-files').css({
                'display': 'inline-block',
                'visibility': 'visible',
                'opacity': '1'
            });
            warning();
            $.ajax({
                type: 'GET',
                url: '/delete/' + data,
                cache: false
            })
            .always(function (data) {
                lastSelected = undefined;
                clearInterval(stopAnimation);
                $('#status-files').fadeOut(1500);
                showMessage(data);
                $('#botones td.butOptional').hide();
                displayTable();
                $('#progressbar').load(document.URL +  ' #progressbar');
            });
		});
	});

    $(function() {
		$('#mover').off('click');
		$('#mover').click(function(){
            var id = $('#body tr.selected').attr("id");
            var name = "";
            for (i = 2; name == "" || i == 10; i++){
                name = $('#body tr.selected').text().split("\n")[i];
                name = $.trim(name);
            }
            if(name!='undefined') {

                var url = document.location.href;
                var separated_url = url.split('/');
                var parent = separated_url[4];
                if(typeof(parent) === 'undefined'){ parent = 'root'; }

                var selected = false;
                var nFolders = 0;
                $("tr").each(function(){
                    if ($(this).hasClass('folder')){
                        nFolders++;
                        if ($(this).attr('row-key') == lastSelected){
                            selected = true;
                        }
                    }
                });

                if(nFolders == 1 && selected && parent == 'root') {
                    var text = {message: gettext('nofolders'), code: 400};
                    showMessage(text);
                } else if($('#body tr.selected').hasClass('sharedFolder')){
                    var text = {message:gettext('moveshared'), code:400};
                    showMessage(text, true);
                } else {
                    window.open('/move/' + id + '/' + name + '/' + parent, 'popup_form', 'location=no,menubar=no,status=no,top=50%,left=50%,height=550,width=750');
                    window.onsubmit = $('#downloadFile, #mover, #renombrar, #borrar').hide();
                }
            }
		});
	});

    $(function() {
		$('#renombrar').off('click');
		$('#renombrar').click(function(){			
            $('#rename-modal').modal({
                show: true
            });           
		});
	});

    $(function() {
		$('#compartir').off('click');
		$('#compartir').click(function(){
            var id = $('#myTable tr.selected').attr("id");
            if(id === undefined) return;
            get_folder_members(id);
            $('#save-member-button').data("folder", id);
            $('#share-folder-modal').modal({
                show: true
            });
		});
	});


	$(function() {
		$.extend($.tablesorter.themes.bootstrap, {			
		    table : 'table table-striped table-hover'
		});			
		$("table").tablesorter({				
			theme : "bootstrap",
			widthFixed: true,
			widgets : [ "uitheme", "zebra" ],
			widgetOptions : {								
			filter_reset : ".reset",
			headers: {
                    		2: {sorter:"shortDate", dateFormat: "ddmmyyyy"}
              		}
	  	    }
	  	});
        $("#myTable").trigger('update');
	});	
	
	$(function(){
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
		        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", csrftoken);
		        }
		    }
		});
	});			
	
	var error = false;
	$(function(){		
		$('#clickable').off('click');
		$('#clickable').click(function()
		{			
			$('#upload-files').click();			
		});				
		$('#upload-files').fileupload({        
	        url: '/upload/',	    
	        sequentialUploads: true,
	        start: function (e, data) {		
	        	error = false;
	        	clearInterval(stopAnimation);
	        	stopAnimation = undefined;
	        	$('#status-files').removeClass('progress-bar-success').css('width','0');
	    		$('#status-files').css({
	    			'display':'inline-block',
	    			'visibility':'visible',
	    			'opacity':'1'
	    		});	    		
	        },	             
	        progress: function (e, data) {
	        	var progress = parseInt(data.loaded / data.total * 100, 10);
	        	$('#status-files').css('width', progress + '%');	        	
	        	if(progress >= 90)
	        	{	        		
	        		$('#status-files').addClass('progress-bar-success');
	        		if(stopAnimation === undefined) warning();
	        	}
	        },
	        stop: function (e) {
	        	clearInterval(stopAnimation);
	        	$('#status-files').fadeOut(1500);
        		$('#status-files').css({
	    			'display':'inline-block',
	    			'visibility':'visible',
	    			'opacity':'1'
	    		}).fadeOut(1500);
		    	if(error)
		    	{
		    		var text = {message:gettext('successUploadFail'), code:400};
		    		showMessage(text, true);
		    	}
		    	else
		    	{
		    		var text = {message:gettext('successUpload'), code:200};
		    		showMessage(text);
		    	}	
		    	error = false;
	        },	        
	        fail: function (e, data) {	
	        	error = true;	        	
	        	showMessage(data.jqXHR);
	        },	
	        done: function (e, data) {		        	
	        	displayTable();
                $('#progressbar').load(document.URL +  ' #progressbar');
                $('#compartir, #downloadFile, #mover, #renombrar, #borrar').hide();
	        }	        
	    });			
	});	
	
	$(function(){		
		$('#save-member-button').off('click');
		$('#save-member-button').on('click', function(event) {
			share_folder($('#save-member-button').data("folder"), $("#folder-members").tagsinput('items'));
            $('#share-folder-modal').modal('hide');
            $('#compartir, #mover, #renombrar, #borrar').hide();
		});        
	});	
		
	$(function(){
		  $('td.showContext').contextMenu('myMenu1', {				  
		      bindings: {		    	  
		        'delete': function () {		
		        	var data = [];			
					$('#body tr.selected').each(function()
					{
						data.push(this.id);			
					});	
					
		        	$.ajax({
		 		        type: 'GET',
		 		        url: '/delete/' + data,
		 		        cache: false
		 		    })		  
		        	.always(function(data)
	    			{
		        		showMessage(data);
		        		$('#botones td.butOptional').hide();
		        		lastSelected = undefined;
		        		displayTable();
                        $('#progressbar').load(document.URL +  ' #progressbar');
	    			});   
		        },
		        'download': function (t) {

                    if ($('#id_encrypt_option').is(':checked')) {
                        var id = t.className.split(' ').pop();
		                document.location.href = '/download/'+id;
                    } else {
                        downloadButton();
                    }
		        },
                'download_anyway': function (t) {
                    $('#file_id').attr("value", lastSelected);
                    $('#id_boton_descarga').click();
		        },
			    'rename': function (t) {		         
                      $('#rename-modal').modal({
                          show: true
                      });		         
		        },
			    'move': function (t) {
			      var str = "root";
		          var name = $.trim($(t).text());
		          var id = t.className.split(' ')[1];
		          $.get( '/move/' + id + '/' + name + '/' +str, function(data)
        		  {
		        	 var nFolders = 0;
                    $("tr").each(function(){
                        if ($(this).hasClass('folder')){
                            nFolders++;
                        }
                    });
                        var url = document.location.href;
                        var separated_url = url.split('/');
                        var parent = separated_url[4];
                        if(typeof(parent) === 'undefined'){ parent = 'root'; }
                    if(nFolders == 0 && parent == 'root'){
                        var text = {message:gettext('nofolders'), code:400};
                        showMessage(text);
                    }
                    else if(data.code === undefined || data.code === 200)
		        	 {
		        		 window.open('/move/' + id + '/' + name + '/' +parent,'popup_form','location=no,menubar=no,status=no,top=50%,left=50%,height=550,width=750');
		        	 }
		        	 else
		        	 {
		        		 showMessage(data);
		        	 }
        		  });
		        }
		      }
		    });
		  $('td.showContext2').contextMenu('myMenu2', {
		      bindings: {
		        'delete2': function() {	   
	        	var data = [];			
				$('#body tr.selected').each(function()
				{
					data.push(this.id);			
				});		
		          $.ajax({
		 		        type: 'GET',
		 		        url: '/delete/' + data,	 		        
		 		        cache: false		 		                
		 		    })		  
		        	.always(function(data)
	    			{
		        		showMessage(data);
		        		$('#botones td.butOptional').hide();
		        		lastSelected = undefined;
		        		displayTable();
                        $('#progressbar').load(document.URL +  ' #progressbar');
	    			});   
		        },
			    'rename2': function (t) {		         
                      $('#rename-modal').modal({
                          show: true
                      });                
		        },
			    'move2': function (t) {
		            var str = "root";
		            var name = $.trim($(t).text());
		            var id = t.className.split(' ').pop();
		            $.get( '/move/' + id + '/' + name + '/' +str, function(data)
        		    {
                        var nFolders = 0;
                        $("tr").each(function(){
                            if ($(this).hasClass('folder')){
                                nFolders++;
                            }
                        });
                        var url = document.location.href;
                        var separated_url = url.split('/');
                        var parent = separated_url[4];
                        if(typeof(parent) === 'undefined'){ parent = 'root'; }
                        if(nFolders == 1 && parent == 'root'){
                            var text = {message:gettext('nofolders'), code:400};
                            showMessage(text);
                        }
                        else if($('#body tr.selected').hasClass('sharedFolder')){
                            var text = {message:gettext('moveshared'), code:400};
                            showMessage(text, true);
                        }
                        else if(data.code === undefined || data.code === 200)
		        	    {
                            window.open('/move/' + id + '/' + name + '/' +str,'popup_form','location=no, menubar=no, status=no, top=50%, left=50%, height=550, width=750');
		        	    }

		        	    else
		        	    {
                            showMessage(data);
                        }
        		    });
		        },
		        'share': function(t){
		        	var id = t.className.split(' ').pop();
		            get_folder_members(id);
		            $('#save-member-button').data("folder", id);
		            $('#share-folder-modal').modal({
		                show: true
		            });
		        }
		      }
		  });
	});

    //Boton de descarga
    $(function() {
		$('#downloadFile').off('click');
		$('#downloadFile').on('click', function(event) {
            if ($('#body tr.selected').hasClass('encrypted')){
                downloadButton();
            } else {
                $('#body tr.selected').each(function () {
                    var id = $('#body tr.selected').attr("id");
                    document.location.href = '/download/' + id;
                });
            }
		});
	});

    $(function(){ checkStatus(); });
}

function createFolder(){
    if($('folder-button').click()) {
        var foldername = $('#foldername').val();
    }
    if (foldername && foldername !== ""){
        $.ajax({
            type: 'GET',
            url: '/newfolder/'+foldername,
            cache: false
        })
        .always(function(data)
        {
            showMessage(data);
            displayTable();
        });
    }
    $('#foldername').val('');
}

function renombrar(){
    if($('rename-file-button').click()) {
        var newName = $('#newname').val();
    }
    if((typeof(newName) !== 'string') || (newName === '')) return;
    var url = document.location.href;
    var separated_url = url.split('/');
    var parent = separated_url[4];
    if(typeof(parent) === 'undefined')
    {
        parent = 'root';
    }
    var id = $('#body tr.selected').prop('id');
    $.ajax({
        type: 'GET',
        url: '/rename/' + id + '/' + btoa(encodeURIComponent(newName)) + '/' + parent,
        cache: false
    })
        .always(function(data)
        {
            if(showMessage(data)) displayTable();
        });
    $('#newname').val('');
}

function show()
{	
	if(lastSelected !== undefined && $('#body tr').hasClass('selected') && $('#body tr.selected').length == 1)
	{			
		$('#tabla_principal').toggleClass('col-md-8');
		if($('#tabla_principal').hasClass('col-md-8'))
		{			
			$('div.metadataFiles').removeClass('col-md-4').hide();
			$('#tabla_metainformacion_' + lastSelected).addClass('col-md-4');
		    $('#tabla_metainformacion_' + lastSelected).show();
		}
		else
		{
		    $('div.metadataFiles').removeClass('col-md-4');
		    $('div.metadataFiles').hide();	
		}
	}
}

function usersShared(json, id)
{
	var obj = $.parseJSON(json);
	var users = '';
	for (i = 0; i < obj.length; i++) { 
		users += obj[i].email + ' ';		
	}
	$('#metadata_' + id + ' tr.filashared td').eq(1).text(users);
}

function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);                
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function get_folder_members(folder){
    $.getJSON( "/members/"+ folder, function( list_of_users ) {
        $('#folder-members').tagsinput('removeAll');
        for(var i = 0; i < list_of_users.length; i++) {
            if (list_of_users.length >= 1) {            	
            	if(list_of_users[i]['is_owner'] !== true)
            		$('#folder-members').tagsinput('add', list_of_users[i]['email']);
            }
        }
    });
}

function csrfSafeMethod(method) {	    
	    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function share_folder(folder, users){	
	if(folder === '' || users === '') return false;
	$.ajax({		
        type: 'POST',    
        data: users,
        url: '/share/' + folder,       
        processData: false,
        contentType: false,
        cache: false
    })		   
    .always(function(data)
    {
    	showMessage(data);
        displayTable();
    });   	
}

function displayTable()
{
	$.get(document.location.href, function(data)
	{
		$('p.navbar-text:eq(1)').replaceWith($(data).find('p.navbar-text:eq(1)'));
		$('div.progress.global:first').replaceWith($(data).find('div.progress.global:first'));
		$('#body').replaceWith($(data).find('#body'));		
		$('div.metadataFiles').not('#tabla_metainformacion_'+lastSelected).remove();
		var tmp = $(data).find('div.metadataFiles').not('#tabla_metainformacion_'+lastSelected).clone();
		$('#tabla_principal').after(tmp);
		$('#metadata_'+lastSelected).replaceWith($(data).find('#metadata_'+lastSelected));
		loadEvents();
	});
}

function showMessage(data, warnning)
{		
	if(data === undefined) return false;
	try {
		data = $.parseJSON(data.responseText);
	}
	catch(e){}	
	if(data.message === undefined || data.message === '') return false;
	if (data.code === 200 || data.code === 201)
	{
		 if(warnning !== undefined && warnning === true)
			 $.jGrowl(data.message, {theme: "jgrowl-warnning", sticky: true});			 
		 else
			 $.jGrowl(data.message, {theme: "jgrowl-success", sticky: false});
         return true;
    }
    else
    {
    	if(warnning !== undefined && warnning === true)
    		$.jGrowl(data.message, {theme: "jgrowl-warnning", sticky: true});
    	else
    		$.jGrowl(data.message, {theme: "jgrowl-error", sticky: false, life: '10000'});
         return true;
    }
	return false;
}

function validepopupform(){
    window.opener.document.form1.text1.value=document.form2.text2.value;
    self.close();
}

function move_element(){
    var url = document.location.href;
    var separated_url = url.split('/');
    var parent_id = separated_url[6];
    var element_id = separated_url[4];
    var element_name = separated_url[5];      
    $.ajax({
	        type: 'GET',
	        url: '/move_element/'+ element_id + '/' + btoa(encodeURIComponent(decodeURIComponent(element_name).trim())) + '/' + parent_id,
	        cache: false	              
	    })		  
	.always(function(data)
	{
    	if(window.opener.showMessage(data)) window.opener.displayTable();
    	window.close();
	});   
}

function selectAll()
{	
	if($('#body tr').hasClass('selected'))
	{		
		$('#botones td.butOptional, #borrar').hide();
        $('#body tr.selected').each(function () {
            $('#body tr.selected').removeClass('selected');
        });
	}
	else
	{
		$('#body tr').addClass('selected');				
		if($('#body tr.selected').length > 1)
		{					
			$('#compartir, #download, #mover, #renombrar').hide();
			$('#borrar').show();
		}	
		else if($('#body tr.selected').hasClass('showContext') && $('#body tr').hasClass('selected'))
		{			
			$('#download, #mover, #renombrar, #borrar').show();
		}
		else if($('#body tr').hasClass('selected'))
		{
			$('#compartir, #mover, #renombrar, #borrar').show();
		}		
	}	
}

//comprobar diálogo de encriptación
function checkStatus() {
    if (!$('#id_encrypt_option').is(':checked')) {
        $("#id_encrypt_pass").val('');
    }
    $('#id_encrypt_option').on('click', function(event) {
        if ($('#id_encrypt_option').is(':checked')) {
            $("#id_encrypt_pass").removeAttr('disabled').attr('required', true);
        } else {
            $("#id_encrypt_pass").val('').removeAttr('required').attr('disabled', true);
        }
    });
}



function saveId(id){
    $('#prompt_pass').modal('show');
    $("#id_encrypt_pass2").attr('required', 'true').val('');
    $('#file_id').attr("value", id);
    $("#last_pass").val(0);

    $('#id_boton_redirect').on('click', function(event) {
        if ($("#id_encrypt_pass2").val() != ""){
            $('#prompt_pass').modal('hide');
        }
    });
}

function downloadButton(){
    $('#prompt_pass').modal('show');
    $("#id_encrypt_pass2").attr('required', 'true').val('');
    $('#file_id').attr("value", lastSelected);
    $("#last_pass").val(0);

    $('#id_boton_redirect').on('click', function(event) {
        if ($("#id_encrypt_pass2").val() != ""){
            $('#prompt_pass').modal('hide');
        }
    });
}

function downloadAnyway(){
    $("#id_encrypt_pass2").removeAttr('required');
    $("#last_pass").val(1);
    $('#prompt_pass').modal('hide');
}

function getPathlist(){

    pathlist = ['root'];
    $('#path a').each(function () {
        var url = $(this).attr('href');
        var separated_url = url.split('/');
        var id = separated_url[separated_url.length-1];
        if(url != '/' && url != ''){
            pathlist.push(id);
        }
    });
    var url = document.URL;
    var separated_url = url.split('/');
    var id = separated_url[separated_url.length-1];
    if(id != ''){ pathlist.push(id); }
    return pathlist;
}

function sendPathlist(){
    var path = getPathlist();
    var path_string = JSON.stringify(path);
    $.ajax({
        type: 'POST',
        url: '/pathlist/',
        data: {path:path_string}
    });
}