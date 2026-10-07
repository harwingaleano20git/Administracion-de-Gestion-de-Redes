// Pausar recarga al editar cualquier formulario; enviar reanuda tras navegar.
if (document.querySelector('[data-auto-refresh]')) {
  let modified=false;
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('input',()=>modified=true);
    form.addEventListener('change',()=>modified=true);
  });
  setInterval(()=>{
    if(!modified && !document.activeElement.closest('form')) window.location.reload();
  },5000);
}
