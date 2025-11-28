from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
import os
from PIL import Image as PILImage
from io import BytesIO
from chatbot import FitProChatbot, ChatMessage
from fitness_calc import calculate_stride_length, calculate_calories_burned

# Android permission helper
def request_activity_recognition_permission():
    """Request ACTIVITY_RECOGNITION permission on Android 10+"""
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        from android.permissions import request_permissions, Permission
        
        # Check if already granted
        request_permissions([Permission.ACTIVITY_RECOGNITION])
        print('[INFO] Requested ACTIVITY_RECOGNITION permission')
        return True
    except Exception as e:
        print(f'[INFO] Permission request not available or already granted: {e}')
        return False

Window.clearcolor = (0.1, 0.1, 0.15, 1)
Window.size = (420, 700)  # Mobile-like, shorter and centered on screen


from kivy.properties import NumericProperty, BooleanProperty


class AnimatedGif(Widget):
    """Display animated GIFs by cycling through PIL frames."""
    source = ''
    
    def __init__(self, source='', **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.frames = []
        self.frame_durations = []
        self.current_frame_index = 0
        self._animation_event = None
        
        # Load GIF on next cycle to ensure widget is ready
        Clock.schedule_once(lambda dt: self._load_gif(), 0.1)
        self.bind(size=self._update_display, pos=self._update_display)
    
    def _load_gif(self):
        """Load all frames from the GIF file."""
        if not self.source or not os.path.exists(self.source):
            print(f'[WARN] GIF file not found: {self.source}')
            return
        
        try:
            gif = PILImage.open(self.source)
            num_frames = getattr(gif, 'n_frames', 1)
            print(f'[INFO] Loading {num_frames} frames from {self.source}')
            
            for i in range(num_frames):
                gif.seek(i)
                # Get frame duration (default 100ms)
                duration = gif.info.get('duration', 100) / 1000.0
                self.frame_durations.append(max(0.05, duration))
                
                # Convert to RGBA
                if gif.mode != 'RGBA':
                    frame = gif.convert('RGBA')
                else:
                    frame = gif.copy()
                
                # Make white/light background transparent (convert white to transparent)
                data = frame.getdata()
                new_data = []
                for item in data:
                    # If pixel is white or very light (R,G,B all > 240), make it transparent
                    if len(item) >= 3 and item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))  # Transparent white
                    else:
                        new_data.append(item)
                
                frame.putdata(new_data)
                
                # Save with transparency preserved
                buf = BytesIO()
                frame.save(buf, format='PNG', optimize=False)
                buf.seek(0)
                
                # Load with Kivy, transparency will be preserved
                kivy_img = CoreImage(buf, ext='png')
                self.frames.append(kivy_img.texture)
            
            print(f'[INFO] Loaded {len(self.frames)} frames with transparent backgrounds')
            # Start animation
            self._start_animation()
        except Exception as e:
            print(f'[ERROR] Failed to load GIF: {e}')
    
    def _start_animation(self):
        """Start the animation loop."""
        if not self.frames:
            return
        if self._animation_event:
            self._animation_event.cancel()
        self.current_frame_index = 0
        self._show_frame(0)
    
    def _show_frame(self, frame_idx):
        """Display a specific frame and schedule the next one."""
        if not self.frames:
            return
        
        self.current_frame_index = frame_idx % len(self.frames)
        self._update_display()
        
        # Schedule next frame
        duration = self.frame_durations[self.current_frame_index]
        self._animation_event = Clock.schedule_once(
            lambda dt: self._show_frame(frame_idx + 1),
            duration
        )
    
    def _update_display(self, *args):
        """Redraw the current frame with transparency support."""
        self.canvas.clear()
        if not self.frames or self.current_frame_index >= len(self.frames):
            return
        
        try:
            texture = self.frames[self.current_frame_index]
            with self.canvas:
                # Use color with full alpha to preserve texture transparency
                Color(1, 1, 1, 1)
                Rectangle(texture=texture, pos=self.pos, size=self.size)
        except Exception as e:
            print(f'[ERROR] Failed to render frame: {e}')


class CircularProgress(Widget):
    """A simple circular progress ring. Set `value` and `max` to control fill."""
    value = NumericProperty(0)
    max = NumericProperty(100)
    thickness = NumericProperty(dp(8))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas,
                  value=self._update_canvas, max=self._update_canvas,
                  thickness=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        r = min(self.width, self.height) / 2.0 - (self.thickness / 2.0)
        if r <= 0:
            return
        # background ring
        with self.canvas:
            Color(0.85, 0.85, 0.85, 1)
            Line(circle=(cx, cy, r, 0, 360), width=self.thickness)
            # progress arc
            try:
                frac = float(self.value) / float(self.max) if float(self.max) > 0 else 0.0
            except Exception:
                frac = 0.0
            angle = max(0.0, min(1.0, frac)) * 360.0
            Color(0.05, 0.4, 0.6, 1)
            Line(circle=(cx, cy, r, 0, angle), width=self.thickness, cap='round')


class FitProInterface(BoxLayout):
    steps = NumericProperty(0)
    goal = NumericProperty(10000)
    running = BooleanProperty(False)
    
    # User fitness data (configure these for accurate calculations)
    USER_HEIGHT_CM = 175  # User's height in cm
    USER_WEIGHT_KG = 70   # User's weight in kg
    USER_GENDER = "male"  # "male" or "female"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._event = None
        # real step sensor / fallback mode
        self._sensor_event = None
        self._use_sensor = False
        self._step_sensor = None
        self._step_sensor_available = False
        
        # try importing plyer step counter (Android native step sensor)
        try:
            from plyer import stepCounter
            self._step_sensor = stepCounter
            self._step_sensor_available = True
            print('[INFO] Step counter sensor available via Plyer')
        except Exception as e:
            print(f'[INFO] Step counter sensor not available: {e}')
            self._step_sensor = None
            self._step_sensor_available = False

    def _update_ui(self):
        # update labels and progress bar (support both old and new kv ids)
        # Steps
        if 'steps_label' in self.ids:
            self.ids.steps_label.text = str(int(self.steps))
        # Goal (new dashboard id)
        if 'goal_value' in self.ids:
            self.ids.goal_value.text = str(int(self.goal))
        # Goal (legacy label id kept for backward compatibility)
        if 'goal_label' in self.ids:
            self.ids.goal_label.text = f'Goal: {int(self.goal)}'
        # Progress bar (if present)
        if 'step_progress' in self.ids:
            try:
                self.ids.step_progress.value = min(self.steps, self.ids.step_progress.max)
            except Exception:
                pass

        # Calculate stride length based on user data
        stride_length_cm = calculate_stride_length(self.USER_HEIGHT_CM, self.USER_GENDER)
        
        # Calories burned estimate using real formula
        if 'calories_value' in self.ids:
            calories = calculate_calories_burned(int(self.steps), self.USER_WEIGHT_KG, stride_length_cm)
            self.ids.calories_value.text = f"{calories:.1f} kcal"

        # Distance estimate (km) using real formula
        if 'distance_value' in self.ids:
            distance_km = (int(self.steps) * stride_length_cm) / 100000
            self.ids.distance_value.text = f"{distance_km:.2f} km"

    def _step_tick(self, dt):
        # simple simulated increment; increment by 1 per tick
        self.steps += 1
        self._update_ui()
        # if goal reached, stop
        if self.steps >= self.goal:
            self.step_stop()

    def _poll_step_sensor(self, dt):
        """Poll the real step counter sensor for step count updates."""
        if not self._step_sensor_available or not self._step_sensor:
            return
        try:
            current_steps = self._step_sensor.steps
            if current_steps is not None:
                self.steps = current_steps
                self._update_ui()
                # stop if reached goal
                if self.steps >= self.goal:
                    self.step_stop()
        except Exception as e:
            print(f'[ERROR] Failed to read step sensor: {e}')

    def step_start(self):
        if not self.running:
            self.running = True
            # prefer real step sensor when available (Android)
            if self._step_sensor_available:
                try:
                    # Request runtime permission on Android 10+ before accessing sensor
                    request_activity_recognition_permission()
                    # enable step counter polling
                    if self._sensor_event is None:
                        self._sensor_event = Clock.schedule_interval(self._poll_step_sensor, 1.0)
                    self._use_sensor = True
                    print('[INFO] Step counter started (real device sensor mode)')
                    return
                except Exception as e:
                    print(f'[WARN] Failed to start real sensor: {e}')
            # fallback to simulation
            self._event = Clock.schedule_interval(self._step_tick, 0.5)
            print('[INFO] Step counter started (simulation mode)')

    def step_stop(self):
        if self.running:
            self.running = False
            if self._use_sensor:
                if self._sensor_event is not None:
                    self._sensor_event.cancel()
                    self._sensor_event = None
                self._use_sensor = False
            if self._event is not None:
                self._event.cancel()
                self._event = None
            print('[INFO] Step counter stopped')

    def step_reset(self):
        # stop and reset
        self.step_stop()
        self.steps = 0
        self._update_ui()
        print('Step counter reset')

    def step_add(self, n=1):
        # manual increment (button)
        self.steps += n
        self._update_ui()

    def set_dashboard(self, instance=None):
        # show the dashboard label, hide stepcounter
        if 'content_display' in self.ids:
            self.ids.content_display.opacity = 1
            self.ids.content_display.disabled = False
        if 'stepcounter' in self.ids:
            self.ids.stepcounter.opacity = 0
            self.ids.stepcounter.disabled = True
        self.ids.content_display.text = "Dashboard: View your overall progress and metrics."
        print("Switched to Dashboard view.")

    def set_workouts(self, instance=None):
        # show the step counter, hide dashboard label
        if 'content_display' in self.ids:
            self.ids.content_display.opacity = 0
            self.ids.content_display.disabled = True
        if 'stepcounter' in self.ids:
            self.ids.stepcounter.opacity = 1
            self.ids.stepcounter.disabled = False
        # initialize UI values
        self._update_ui()
        print("Switched to Workouts view.")

    def set_profile(self, instance=None):
        # hide stepcounter and show profile text
        if 'content_display' in self.ids:
            self.ids.content_display.opacity = 1
            self.ids.content_display.disabled = False
        if 'stepcounter' in self.ids:
            self.ids.stepcounter.opacity = 0
            self.ids.stepcounter.disabled = True
        self.ids.content_display.text = "Profile: Manage your personal details and goals."
        print("Switched to Profile view.")


class SplashScreen(Screen):
    def __init__(self, image_source='finess_bg.jpg', **kwargs):
        super().__init__(**kwargs)
        # use a FloatLayout so we can overlay the label over the image
        self.name = 'splash'
        fl = FloatLayout()

        # use provided splash image as background (use texture rectangle)
        img_path = image_source if os.path.isabs(image_source) else os.path.join(os.path.dirname(__file__), image_source)
        if not os.path.exists(img_path):
            img_path = os.path.join(os.path.dirname(__file__), 'finess_bg.jpg')
        try:
            tex = CoreImage(img_path).texture
            with fl.canvas:
                self._bg_rect = Rectangle(texture=tex, pos=fl.pos, size=fl.size)
            def _update_bg(instance, value):
                self._bg_rect.pos = fl.pos
                self._bg_rect.size = fl.size
            fl.bind(pos=_update_bg, size=_update_bg)
        except Exception:
            # fallback to solid color
            with fl.canvas:
                Color(0.06, 0.06, 0.07, 1)
                self._bg_rect = Rectangle(pos=fl.pos, size=fl.size)
            def _update_bg(instance, value):
                self._bg_rect.pos = fl.pos
                self._bg_rect.size = fl.size
            fl.bind(pos=_update_bg, size=_update_bg)

        # styled app title at bottom center (use project TTF if present)
        font_path = None
        candidates = [
            os.path.join(os.path.dirname(__file__), 'BMEULJIROTTF.ttf'),
            os.path.join(os.path.dirname(__file__), 'fonts', 'BMEULJIROTTF.ttf'),
            os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'BMEULJIROTTF.ttf'),
        ]
        for c in candidates:
            if os.path.exists(c):
                font_path = c
                break

        title = Label(
            text='FITPRO',
            markup=True,
            font_name=font_path if font_path else 'Roboto',
            font_size='44sp',
            size_hint=(1, None),
            height=dp(100),
            pos_hint={'x': 0, 'y': 0},
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        title.text_size = (self.width, None)
        fl.add_widget(title)

        self.add_widget(fl)


class ChatbotScreen(Screen):
    """Screen for the AI chatbot interface"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'chatbot'
        
        # Initialize chatbot: read API key from environment for safety
        # Set the environment variable `FITPRO_GEMINI_API_KEY` before running
        # Example (PowerShell temporary session): $env:FITPRO_GEMINI_API_KEY="your-key"
        import os
        CHATBOT_API_KEY = os.environ.get("FITPRO_GEMINI_API_KEY")
        
        # Fallback: use hardcoded key if env var not set
        if not CHATBOT_API_KEY:
            CHATBOT_API_KEY = "AIzaSyCEJEUGfmWeDdDF9JZSK2kVvCoSCsqGf-4"
        
        # If no key provided, FitProChatbot will use offline fallback responses
        self.chatbot = FitProChatbot(api_key=CHATBOT_API_KEY)
        self.messages: list = []
        
        # Main layout with proper sizing
        main_layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        
        # Chat display area (takes 70% of screen)
        self.scroll_view = ScrollView(size_hint_y=0.70)
        self.chat_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(5))
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll_view.add_widget(self.chat_layout)
        main_layout.add_widget(self.scroll_view)
        
        # Input area (20% of screen)
        input_layout = BoxLayout(size_hint_y=0.20, spacing=dp(5))
        self.text_input = TextInput(
            multiline=False,
            hint_text='Ask me about fitness...',
            size_hint_x=0.85,
            background_color=(0.95, 0.95, 0.95, 1)
        )
        input_layout.add_widget(self.text_input)
        
        # Send button with image - circular and properly sized
        send_btn = Button(
            size_hint_x=0.12,
            background_normal='SEND.png',
            background_down='SEND.png',
            border=(0, 0, 0, 0)
        )
        send_btn.bind(on_press=self.send_message)
        input_layout.add_widget(send_btn)
        
        main_layout.add_widget(input_layout)
        
        # Back to Dashboard button (10% of screen)
        back_btn = Button(text='← Back to Dashboard', size_hint_y=0.10, background_color=(0.2, 0.6, 0.9, 1))
        back_btn.bind(on_press=self.go_to_dashboard)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        
        # Add welcome message
        self._add_bot_message("👋 Hi! I'm your FitPro fitness assistant. Ask me anything about fitness, workouts, nutrition, or motivation!")
    
    def go_to_dashboard(self, instance):
        """Return to dashboard"""
        self.manager.current = 'main'
    
    def send_message(self, instance):
        """Send a message to the chatbot"""
        message_text = self.text_input.text.strip()
        if not message_text:
            return
        
        # Add user message to UI
        self._add_user_message(message_text)
        self.text_input.text = ''
        
        # Get bot response
        response = self.chatbot.get_response(message_text)
        self._add_bot_message(response.message)
    
    def _add_user_message(self, text: str):
        """Add a user message to the chat display"""
        msg_label = Label(
            text=text,
            size_hint_y=None,
            markup=True,
            text_size=(self.chat_layout.width - dp(30), None)
        )
        msg_label.bind(texture_size=lambda *args: setattr(msg_label, 'height', msg_label.texture_size[1] + dp(10)))
        self.chat_layout.add_widget(msg_label)
        Clock.schedule_once(lambda dt: self.scroll_view.scroll_to(msg_label), 0.1)
    
    def _add_bot_message(self, text: str):
        """Add a bot message to the chat display"""
        msg_label = Label(
            text=f'[b]Assistant:[/b]\n{text}',
            size_hint_y=None,
            markup=True,
            text_size=(self.chat_layout.width - dp(30), None)
        )
        msg_label.bind(texture_size=lambda *args: setattr(msg_label, 'height', msg_label.texture_size[1] + dp(10)))
        self.chat_layout.add_widget(msg_label)
        Clock.schedule_once(lambda dt: self.scroll_view.scroll_to(msg_label), 0.1)


class FitProApp(App):
    def build(self):
        # decide image file name (use the file in workspace if present)
        workspace_dir = os.path.dirname(__file__)
        # default filename we detected / suggested
        candidates = ['fitness_bg.jpg', 'fitness_bg.png', 'finess_bg.jpg', 'finess_bg.png']
        found = None
        for c in candidates:
            p = os.path.join(workspace_dir, c)
            if os.path.exists(p):
                found = c
                break

        image_source = found if found else candidates[0]

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(image_source=image_source))

        # main screen contains the FitProInterface which is defined in KV
        main_screen = Screen(name='main')
        # create and keep a reference to the main interface so we can initialize it after splash
        self.main_interface = FitProInterface()
        main_screen.add_widget(self.main_interface)
        sm.add_widget(main_screen)
        
        # Add chatbot screen
        sm.add_widget(ChatbotScreen())

        # schedule switch to main after 2 seconds (typical splash duration)
        Clock.schedule_once(lambda dt: self._switch_to_main(sm), 2.0)
        
        # auto-start step tracking on app launch (for Android auto-tracking)
        Clock.schedule_once(lambda dt: self._start_auto_tracking(self.main_interface), 2.5)

        return sm

    def _switch_to_main(self, sm: ScreenManager):
        sm.current = 'main'

    def _start_auto_tracking(self, interface):
        """Auto-start step tracking when app launches."""
        try:
            interface.step_start()
        except Exception as e:
            print(f'[WARN] Failed to auto-start tracking: {e}')


if __name__ == '__main__':
    FitProApp().run()
