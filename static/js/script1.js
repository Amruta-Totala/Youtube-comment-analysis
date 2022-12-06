<script type="text/javascript">
$(function(){
    
    var twoToneButton = document.querySelector('.twoToneButton');
    
    twoToneButton.addEventListener("click", function() {
        twoToneButton.innerHTML = "Signing In";
        twoToneButton.classList.add('spinning');
        
      setTimeout( 
            function  (){  
                twoToneButton.classList.remove('spinning');
                twoToneButton.innerHTML = "Sign In";
                
            }, 6000);
    }, false);
    
});
</script>