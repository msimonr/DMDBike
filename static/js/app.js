async function actualizar() {
    try {
    const res = await fetch('/stats');
    const data = await res.json();
    const kmNum = Math.round(data.km * 10000) / 10000;
    if(kmNum < 1){
        const metros = Math.round(kmNum * 1000); // 0.734 km -> 734 m
        document.getElementById('km').textContent = metros + " m";
    }else{
        document.getElementById('km').textContent = kmNum.toFixed(2) + " km";
    }
    } catch (e) {
    console.log("Error al actualizar", e);
    }
}


async function actualizarSesionRandom() {
    try {
        const res = await fetch('/random_session');
        const data = await res.json();
    if (!data.ok) return;
        const cont = document.getElementById('random-sesion');
        cont.innerHTML = `
            <div>
            <strong>${data.nombre || "Sin nombre"}</strong><br>
            ${Number(data.km).toFixed(2)} km<br>
            <small>${data.creado_en}</small><br>
            ${data.foto ? `<img src="${data.foto}" style="width:80px;height:80px;object-fit:cover;border-radius:6px;margin-top:4px;">` : ""}
            </div>
        `;
    } catch (e) {
        console.log("Error obteniendo sesión random", e);
    }
}

setInterval(actualizar, 1000);
setInterval(actualizarSesionRandom, 5000);
actualizarSesionRandom();