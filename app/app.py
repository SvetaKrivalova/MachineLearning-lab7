import os
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import shutil
import sys
from sklearn.model_selection import train_test_split

app = Flask(__name__)
app.secret_key = os.urandom(24)

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

FILE_CSV = os.path.join(base_path, 'files_data.csv')
DATASETS_CSV = os.path.join(base_path, 'datasets_data.csv')

if not os.path.exists(FILE_CSV):
    pd.DataFrame(columns=['id', 'photo', 'txt', 'photo_date']).to_csv(FILE_CSV, index=False)

if not os.path.exists(DATASETS_CSV):
    pd.DataFrame(columns=['id', 'dataset_path']).to_csv(DATASETS_CSV, index=False)

destination_dataset_folder = os.path.join(base_path, "datasets")
if not os.path.exists(destination_dataset_folder):
    os.makedirs(destination_dataset_folder)

images_dir = os.path.join(base_path, "images")
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

static_dir = os.path.join(os.path.dirname(__file__), "static", "images")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

def copy_images_to_static():
    for filename in os.listdir(images_dir):
        source_file = os.path.join(images_dir, filename)
        destination_file = os.path.join(static_dir, filename)
        if os.path.isfile(source_file):
            shutil.copy2(source_file, destination_file)

copy_images_to_static()


@app.route('/')
def index():
    files = pd.read_csv(FILE_CSV)
    datasets = pd.read_csv(DATASETS_CSV)
    non_empty_count = files['txt'].notnull().sum()
    non_empty = files[files['txt'].notnull()]

    return render_template('index.html', files=files.to_dict(orient='records'), non_empty=non_empty.to_dict(orient='records'), non_empty_count=non_empty_count, datasets=datasets.to_dict(orient='records'))

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "", 400
    
    files = request.files.getlist('files')

    new_entries = []
    image_files = set() 

    for file in files:
        if file.filename == '':
            return "", 400
        
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        file_path = os.path.join(images_dir, filename)
        
        try:
            file.save(file_path)
            if file_extension != '.txt':
                image_files.add(filename)
        except Exception as e:
            print(f"{e}")
            return "", 500

    for file in files:
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        absolute_path = os.path.abspath(os.path.join(images_dir, filename)).replace("\\", "/")

        if file_extension != '.txt':
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_file_path = os.path.join(images_dir, txt_filename)

            if os.path.exists(txt_file_path):
                absolute_txt_path = os.path.abspath(txt_file_path).replace("\\", "/")
                new_entries.append({
                    'photo': absolute_path,
                    'txt': absolute_txt_path,
                    'photo_date': datetime.now()
                })
            else:
                new_entries.append({
                    'photo': absolute_path,
                    'txt': None, 
                    'photo_date': datetime.now()
                })

        elif file_extension == '.txt':
            for ext in ['.jpg', '.jpeg', '.png']:
                image_filename = os.path.splitext(filename)[0] + ext
                image_path = os.path.join(images_dir, image_filename)

                if os.path.exists(image_path):
                    corresponding_image_path = os.path.abspath(image_path).replace("\\", "/")
                    new_entries.append({
                        'photo': corresponding_image_path,
                        'txt': absolute_path, 
                        'photo_date': datetime.now()
                    })
                    break

    try:
        if os.path.exists(FILE_CSV):
            files_df = pd.read_csv(FILE_CSV)
        else:
            files_df = pd.DataFrame(columns=['id', 'photo', 'txt', 'photo_date'])

        if new_entries:
            new_entries_df = pd.DataFrame(new_entries)
            files_df = pd.concat([files_df, new_entries_df], ignore_index=True)

        files_df.drop_duplicates(subset=['photo'], keep='last', inplace=True)
        files_df.reset_index(drop=True, inplace=True)
        files_df['id'] = range(1, len(files_df) + 1) 
        files_df.to_csv(FILE_CSV, index=False) 
    except Exception as e:
        print(f"{e}")
        return "", 500
    
    for filename in os.listdir(images_dir):
        source_file = os.path.join(images_dir, filename)
        destination_file = os.path.join(static_dir, filename)
        shutil.copy(source_file, destination_file)

    return redirect(url_for('index'))

@app.route('/copy_photos', methods=['POST'])
def copy_photos():
    num_photos = request.form.get('num_photos', type=int)
    dataset_name = request.form.get('dataset_name')
    train_size = request.form.get('train_size', type=float)
    val_size = request.form.get('val_size', type=float)

    datasets_df = pd.read_csv(DATASETS_CSV)
    new_dataset_id = len(datasets_df) + 1
    new_dataset = {
        'id': new_dataset_id,
        'dataset_path': os.path.abspath(os.path.join(destination_dataset_folder, dataset_name)).replace("\\", "/")
    }

    dataset_folder_base = os.path.join(destination_dataset_folder, dataset_name)
    dataset_folder = os.path.join(destination_dataset_folder, dataset_name, "dataset")
    os.makedirs(dataset_folder_base, exist_ok=True)
    os.makedirs(dataset_folder, exist_ok=True)

    files_df = pd.read_csv(FILE_CSV)

    files_df['txt_exists'] = files_df['photo'].apply(lambda x: os.path.exists(os.path.join(os.path.dirname(__file__), "Images", os.path.splitext(x)[0] + '.txt')))
    files_df_filtered = files_df[files_df['txt_exists']]

    if num_photos is not None:
        selected_photos = files_df_filtered.sample(n=num_photos, random_state=1)
    else:
        selected_photos = files_df_filtered

    for _, row in selected_photos.iterrows():
        photo_path = os.path.join(os.path.dirname(__file__), "Images", row['photo'])
        shutil.copy(photo_path, dataset_folder)

        txt_file = os.path.splitext(row['photo'])[0] + '.txt'
        if os.path.exists(os.path.join(os.path.dirname(__file__), "Images", txt_file)):
            shutil.copy(os.path.join(os.path.dirname(__file__), "Images", txt_file), dataset_folder)

    split_and_save_dataset(dataset_folder, dataset_folder_base, test_size=val_size)

    datasets_df = pd.read_csv(DATASETS_CSV)
    new_dataset_df = pd.DataFrame([new_dataset])
    datasets_df = pd.concat([datasets_df, new_dataset_df], ignore_index=True)
    datasets_df.to_csv(DATASETS_CSV, index=False)

    return redirect(url_for('index'))

def split_and_save_dataset(source_folder, destination_folder, test_size):
    all_files = os.listdir(source_folder)

    images = [f for f in all_files if f.endswith(('.jpg', '.jpeg', '.png'))]
    texts = [f for f in all_files if f.endswith('.txt')]

    images_with_texts = [img for img in images if os.path.splitext(img)[0] + '.txt' in texts]

    train_files, val_files = train_test_split(images_with_texts, test_size=test_size, random_state=42)

    train_folder = os.path.join(destination_folder, 'train')
    val_folder = os.path.join(destination_folder, 'val')

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    for file in train_files:
        shutil.copy(os.path.join(source_folder, file), os.path.join(train_folder, file))
        
        txt_file = os.path.splitext(file)[0] + '.txt'
        if txt_file in texts:
            shutil.copy(os.path.join(source_folder, txt_file), os.path.join(train_folder, txt_file))

    for file in val_files:
        shutil.copy(os.path.join(source_folder, file), os.path.join(val_folder, file))
        
        txt_file = os.path.splitext(file)[0] + '.txt'
        if txt_file in texts:
            shutil.copy(os.path.join(source_folder, txt_file), os.path.join(val_folder, txt_file))

@app.route('/create_class', methods=['POST'])
def create_class():
    selected_dataset = request.form.get('selected_dataset')
    class_name = request.form.get('class_name')

    if selected_dataset and class_name:
        dataset_folder = os.path.join(destination_dataset_folder, selected_dataset)
        classes_file_path = os.path.join(dataset_folder, 'classes.txt').replace("\\", "/")
        data_yaml_path = os.path.join(dataset_folder, 'data.yaml').replace("\\", "/")

        try:
            with open(classes_file_path, 'a') as f:
                f.write(class_name + '\n')
        except Exception as e:
            print(f"{e}")

        try:
            with open(classes_file_path, 'r') as f:
                class_names = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"{e}")
            class_names = []

        num_classes = len(class_names)

        try:
            with open(data_yaml_path, 'w') as f:
                f.write(f"train: ./train\n")
                f.write(f"val: ./val\n")
                f.write(f"nc: {num_classes}\n")
                f.write(f"names: {class_names}\n")
        except Exception as e:
            print(f"{e}")
    
    return '', 204 

@app.route('/create_train_script', methods=['POST'])
def create_train_script():
    try:
        imgsz = int(request.form['imgsz'])
        epochs = int(request.form['epochs'])
        batch = int(request.form['batch'])
        save_period = int(request.form['save_period'])
        selected_dataset = request.form['selected_dataset']

        if not selected_dataset.endswith(os.path.sep):
            selected_dataset += os.path.sep

        script_path = os.path.join(selected_dataset, 'train.py')
        abs_selected_dataset = os.path.abspath(selected_dataset)

        script_content = f"""import torch
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO('yolo11n.pt')
    results = model.train( 
        data='{(os.path.join(abs_selected_dataset, 'data.yaml')).replace("\\", "\\\\")}',   
        imgsz={imgsz},
        epochs={epochs},
        batch={batch},
        save_period={save_period}
    )
"""

        with open(script_path, 'w') as f:
            f.write(script_content)

    except Exception as e:
        print(f"{e}")

    return '', 204 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)