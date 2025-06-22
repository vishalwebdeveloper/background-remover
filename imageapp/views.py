from django.shortcuts import render
from .models import EditedImage
from .forms import ImageUploadForm
from rembg import remove
from PIL import Image
from django.core.files.base import ContentFile
from django.utils import timezone
import io,os

# Cleanup expired images (older than 24 hrs)
def cleanup_old_images():
    expired_images = EditedImage.objects.all()
    for image in expired_images:
        if image.is_expired():
            try:
                if image.original_image and os.path.isfile(image.original_image.path):
                    os.remove(image.original_image.path)
                if image.removed_bg_image and os.path.isfile(image.removed_bg_image.path):
                    os.remove(image.removed_bg_image.path)
                if image.edited_image and os.path.isfile(image.edited_image.path):
                    os.remove(image.edited_image.path)
            except Exception as e:
                print(f"Error deleting files: {e}")
            image.delete()

def upload_image(request):
    # Delete old images older than 24 hours
    # for img in EditedImage.objects.all():
    #     if img.is_expired():
    #         img.delete_files_and_self()
    cleanup_old_images()

    uploaded = None
    edited = None
    form = ImageUploadForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                instance = form.save()
                input_image = Image.open(instance.original_image).convert("RGBA")
                bg_removed = remove(input_image)
                buffer = io.BytesIO()
                bg_removed.save(buffer, format='PNG')
                instance.removed_bg_image.save('removed.png', ContentFile(buffer.getvalue()), save=True)
                uploaded = instance

        elif action == 'edit':
            image_id = request.POST.get('image_id')
            instance = EditedImage.objects.get(id=image_id)
            bg_type = request.POST.get('bg_type')

            foreground = Image.open(instance.removed_bg_image.path).convert("RGBA")

            if bg_type == 'color':
                bg_color = request.POST.get('bg_color')
                background = Image.new("RGBA", foreground.size, bg_color)
            elif bg_type == 'image':
                bg_file = request.FILES.get('bg_image')
                bg = Image.open(bg_file)
                background = bg.resize(foreground.size).convert("RGBA")
            else:
                background = Image.new("RGBA", foreground.size, (255, 255, 255, 255))

            combined = Image.alpha_composite(background, foreground)
            buffer = io.BytesIO()
            combined.save(buffer, format='PNG')
            instance.edited_image.save(f'edited_{timezone.now().timestamp()}.png', ContentFile(buffer.getvalue()), save=True)
            edited = instance
            uploaded = instance  # Keep the removed background visible too

    return render(request, 'upload.html', {
        'form': form,
        'uploaded': uploaded,
        'edited': edited,
    })
