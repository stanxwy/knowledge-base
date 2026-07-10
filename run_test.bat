echo "how to tell if an attr belongs to class or instance"
python -m app.test.00_class_or_instance_field

echo "system environment variables take precedence over .env values unless override=True is set."
python -m app.test.01_loadenv_vs_sysenv

echo "override dict value using dict.update(**new_obj)"
python -m app.test.02_config_update