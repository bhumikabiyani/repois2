from django.test import TestCase
# from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from SGPA.apps.home.views import *
from SGPA.apps.proyectos.views import *
from SGPA.apps.roles.views import *
from SGPA.apps.usuario.views import *
from SGPA.apps.flujo.views import *
from SGPA.apps.actividades.views import *
from SGPA.apps.sprint.views import *
from SGPA.apps.userhistory.views import *
import unittest
import django
django.setup()

class UserTestCase(TestCase):

    def setUp(self):
        self.u1 = User.objects.create(username="cgonza",first_name="Carlos",last_name="Gonzalez",email="cgonzalez@gmail.com")
        self.p1 = Proyecto.objects.create(nombrelargo="prueba", usuario_lider = self.u1, cantidad = "10", estado = "1")
        self.f1 = Flujo.objects.create(nombre="flujo1")
        self.a1 = Actividad.objects.create(nombre="act1")
        self.a2 = Actividad.objects.create(nombre="act2")
        self.fa1 = FlujoActividad.objects.create(flujo = self.f1, actividad = self.a1, orden = 1)
        self.fa2 = FlujoActividad.objects.create(flujo = self.f1, actividad = self.a2, orden = 2)
        self.fap1 = FlujoActividadProyecto.objects.create(flujo = self.f1, actividad = self.a1, proyecto = self.p1, orden = 1)
        self.fap2 = FlujoActividadProyecto.objects.create(flujo = self.f1, actividad = self.a2, proyecto = self.p1, orden = 2)
        self.r1 = Rol.objects.get(id=2)
        self.s1 = Sprint.objects.create(nombre="Sprint8",descripcion="prueba",proyecto=self.p1)
        self.us1 = UserHistory.objects.create(nombre="US1",proyecto=self.p1,encargado=self.u1)
        self.urp = UsuarioRolProyecto.objects.create(proyecto = self.p1,usuario = self.u1,rol = self.r1)

    def testLogin_View(self):
        request = RequestFactory().get('/usuario')
        request.user = self.u1
        response = login_view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def testRecuperarPass_View(self):
        request = RequestFactory().get('/usuario')
        response = recuperarcontrasena_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCreateRolSist_View(self):
        request = RequestFactory().get('/roles')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_rolS(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCreateRolProy_View(self):
        request = RequestFactory().get('/roles')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_rolP(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="admin")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = mod_rol(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = borrar_rol(request, '2')
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCreateUser(self):
        user = User.objects.get(username="cgonza")
        self.assertEqual(user.get_username(),"cgonza")

    def testAddUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crearUsuario_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = mod_user(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = eliminar_usuario(request,"1")
        # Check.
        self.assertEqual(response.status_code, 302)

    def testUnDelUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = activar_usuario(request,"1")
        # Check.
        self.assertEqual(response.status_code, 302)

    def testViewUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = visualizar_usuario(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)

    def testChangePass_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = cambiar_password(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearProyecto_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_proyecto(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModProyecto_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        proy = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = mod_proyecto(request,proy.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAsigMiembro_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        proy = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = asignar_miembro(request,proy.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAsigFlujo_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        proy = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = asignar_flujo(request,proy.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearFlujo_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_flujo(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModFlujo_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        request.user = user
        response = mod_flujo(request,flujo.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelFlujo_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        request.user = user
        response = borrar_flujo(request,flujo.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearActividad_View(self):
        request = RequestFactory().get('/actividades')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_actividad(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModActividad_View(self):
        request = RequestFactory().get('/actividades')
        user = User.objects.get(username="cgonza")
        actividad = Actividad.objects.get(nombre="act1")
        request.user = user
        response = mod_actividad(request,actividad.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelActividad_View(self):
        request = RequestFactory().get('/actividades')
        user = User.objects.get(username="cgonza")
        actividad = Actividad.objects.get(nombre="act1")
        request.user = user
        response = borrar_actividad(request,actividad.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAsigAct_Flujo_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        request.user = user
        response = asignar_actividades(request,flujo.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testBorrarMiembro_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        urp = UsuarioRolProyecto.objects.get(proyecto=self.p1,rol=self.r1,usuario=self.u1)
        request.user = user
        response = borrar_miembro(request,urp.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAsigAct_Proy_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = asignar_actividad_proy(request,flujo.id,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearSprint_View(self):
        request = RequestFactory().get('/Sprint')
        user = User.objects.get(username="cgonza")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = crear_sprint(request,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModSprint_View(self):
        request = RequestFactory().get('/sprint')
        user = User.objects.get(username="cgonza")
        sprint = Sprint.objects.get(nombre="Sprint8")
        request.user = user
        response = mod_sprint(request,sprint.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelSprint_View(self):
        request = RequestFactory().get('/sprint')
        user = User.objects.get(username="cgonza")
        sprint = Sprint.objects.get(nombre="Sprint8")
        request.user = user
        response = borrar_sprint(request,sprint.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearUserStorie_View(self):
        request = RequestFactory().get('/userhistory')
        user = User.objects.get(username="cgonza")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = crear_user_history(request,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModUserStorie_View(self):
        request = RequestFactory().get('/userhistory')
        user = User.objects.get(username="cgonza")
        us = UserHistory.objects.get(nombre="US1")
        request.user = user
        response = mod_user_history(request,us.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelUserStorie_View(self):
        request = RequestFactory().get('/userhistory')
        user = User.objects.get(username="cgonza")
        us = UserHistory.objects.get(nombre="US1")
        request.user = user
        response = borrar_user_history(request,us.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testSubirActividad(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        actividad = Actividad.objects.get(nombre="act2")
        request.user = user
        response = subir_actividad(request,flujo.id,actividad.id)
        # Check.
        self.assertEqual(response.status_code, 302)

    def testBajarActividad(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        actividad = Actividad.objects.get(nombre="act1")
        request.user = user
        response = bajar_actividad(request,flujo.id,actividad.id)
        # Check.
        self.assertEqual(response.status_code, 302)

    def testVerAct_Proy_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = ver_actividades_proyecto(request,flujo.id,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testSubirActividad_Proyecto(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        actividad = Actividad.objects.get(nombre="act2")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = subir_actividad_proyecto(request,flujo.id,actividad.id,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 302)

    def testBajarActividad_Proyecto(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        actividad = Actividad.objects.get(nombre="act1")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = bajar_actividad_proyecto(request,flujo.id,actividad.id,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 302)

    def testVerKanban_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="flujo1")
        proyecto = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = visualizar_kanban(request,flujo.id,proyecto.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testVer_log_userHistory_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        us = UserHistory.objects.get(nombre="US1")
        request.user = user
        response = ver_log_user_history(request,us.id)
        # Check.
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()