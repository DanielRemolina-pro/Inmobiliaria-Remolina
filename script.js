document.addEventListener('DOMContentLoaded', function() {
    const botonesVerDetalles = document.querySelectorAll('.propiedad-card button');
    const btnVolver = document.getElementById('btn-volver');
    const btnVerPropiedades = document.getElementById('btn-ver-propiedades');
    const vistaDetalles = document.getElementById('vista-detalles');
    const hero = document.getElementById('hero');
    const propiedadesSection = document.getElementById('propiedades');
    const contactoSection = document.getElementById('contacto');

    function mostrarDetalles(tarjeta) {
        document.getElementById('propiedad-titulo').textContent = tarjeta.querySelector('h3').textContent;
        document.getElementById('propiedad-precio').textContent = tarjeta.querySelector('.precio').textContent;
        document.getElementById('propiedad-descripcion').textContent = tarjeta.querySelector('.descripcion').textContent;
        document.getElementById('propiedad-imagen').src = tarjeta.querySelector('img').src;
        document.getElementById('propiedad-imagen').alt = tarjeta.querySelector('img').alt;
        
        hero.classList.add('oculto');
        propiedadesSection.classList.add('oculto');
        contactoSection.classList.add('oculto');
        vistaDetalles.classList.remove('oculto');
        
        window.scrollTo(0, 0);
    }

    function volver() {
        vistaDetalles.classList.add('oculto');
        hero.classList.remove('oculto');
        propiedadesSection.classList.remove('oculto');
        contactoSection.classList.remove('oculto');
        
        localStorage.removeItem('vistaActual');
        localStorage.removeItem('datosPropiedad');
    }

    botonesVerDetalles.forEach(function(boton) {
        boton.addEventListener('click', function() {
            const tarjeta = this.parentElement;
            
            mostrarDetalles(tarjeta);
            
            localStorage.setItem('vistaActual', 'detalles');
            localStorage.setItem('datosPropiedad', JSON.stringify({
                titulo: tarjeta.querySelector('h3').textContent,
                precio: tarjeta.querySelector('.precio').textContent,
                descripcion: tarjeta.querySelector('.descripcion').textContent,
                imagen: tarjeta.querySelector('img').src,
                alt: tarjeta.querySelector('img').alt
            }));
        });
    });

    btnVolver.addEventListener('click', volver);

    btnVerPropiedades.addEventListener('click', function() {
        propiedadesSection.scrollIntoView({ behavior: 'smooth' });
    });

    if (localStorage.getItem('vistaActual') === 'detalles') {
        const datos = JSON.parse(localStorage.getItem('datosPropiedad'));
        if (datos) {
            document.getElementById('propiedad-titulo').textContent = datos.titulo;
            document.getElementById('propiedad-precio').textContent = datos.precio;
            document.getElementById('propiedad-descripcion').textContent = datos.descripcion;
            document.getElementById('propiedad-imagen').src = datos.imagen;
            document.getElementById('propiedad-imagen').alt = datos.alt;
            
            hero.classList.add('oculto');
            propiedadesSection.classList.add('oculto');
            contactoSection.classList.add('oculto');
            vistaDetalles.classList.remove('oculto');
        }
    }
});
