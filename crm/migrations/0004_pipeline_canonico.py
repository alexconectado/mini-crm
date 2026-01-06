from django.db import migrations, models


STATUS_MAP = {
    'a_trabalhar': 'conta_para_contato',
    'contato_realizado': 'contato_feito',
    'interesse': 'negociacao_cotacao',
    'pedido': 'pedido_realizado',
    'arquivado': 'arquivada',
}


def map_status_forward(apps, schema_editor):
    Registro = apps.get_model('crm', 'RegistroComercial')
    Historico = apps.get_model('crm', 'ContatoHistorico')

    for registro in Registro.objects.all():
        novo = STATUS_MAP.get(registro.status_pipeline)
        if novo and registro.status_pipeline != novo:
            registro.status_pipeline = novo
            registro.save(update_fields=['status_pipeline'])

    for contato in Historico.objects.all():
        antigo, novo = contato.status_anterior, contato.status_novo
        mudou = False
        if antigo in STATUS_MAP:
            contato.status_anterior = STATUS_MAP[antigo]
            mudou = True
        if novo in STATUS_MAP:
            contato.status_novo = STATUS_MAP[novo]
            mudou = True
        if mudou:
            contato.save(update_fields=['status_anterior', 'status_novo'])


def map_status_backward(apps, schema_editor):
    reverse_map = {v: k for k, v in STATUS_MAP.items()}
    Registro = apps.get_model('crm', 'RegistroComercial')
    Historico = apps.get_model('crm', 'ContatoHistorico')

    for registro in Registro.objects.all():
        antigo = reverse_map.get(registro.status_pipeline)
        if antigo and registro.status_pipeline != antigo:
            registro.status_pipeline = antigo
            registro.save(update_fields=['status_pipeline'])

    for contato in Historico.objects.all():
        antigo, novo = contato.status_anterior, contato.status_novo
        mudou = False
        if antigo in reverse_map:
            contato.status_anterior = reverse_map[antigo]
            mudou = True
        if novo in reverse_map:
            contato.status_novo = reverse_map[novo]
            mudou = True
        if mudou:
            contato.save(update_fields=['status_anterior', 'status_novo'])


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_canal_contato'),
    ]

    operations = [
        migrations.AddField(
            model_name='contatohistorico',
            name='checklist_itens',
            field=models.JSONField(blank=True, default=list, help_text='Checklist aplicado no contato (parcial ou completo)', verbose_name='Checklist marcado'),
        ),
        migrations.AlterField(
            model_name='contatohistorico',
            name='status_anterior',
            field=models.CharField(choices=[('conta_para_contato', 'Conta para Contato'), ('contato_feito', 'Contato Feito'), ('negociacao_cotacao', 'Negociação / Cotação'), ('pedido_realizado', 'Pedido Realizado'), ('conta_ativa', 'Conta Ativa (Recorrência)'), ('arquivada', 'Arquivada')], max_length=30, verbose_name='Status Anterior'),
        ),
        migrations.AlterField(
            model_name='contatohistorico',
            name='status_novo',
            field=models.CharField(choices=[('conta_para_contato', 'Conta para Contato'), ('contato_feito', 'Contato Feito'), ('negociacao_cotacao', 'Negociação / Cotação'), ('pedido_realizado', 'Pedido Realizado'), ('conta_ativa', 'Conta Ativa (Recorrência)'), ('arquivada', 'Arquivada')], max_length=30, verbose_name='Status Novo'),
        ),
        migrations.AlterField(
            model_name='registrocomercial',
            name='status_pipeline',
            field=models.CharField(choices=[('conta_para_contato', 'Conta para Contato'), ('contato_feito', 'Contato Feito'), ('negociacao_cotacao', 'Negociação / Cotação'), ('pedido_realizado', 'Pedido Realizado'), ('conta_ativa', 'Conta Ativa (Recorrência)'), ('arquivada', 'Arquivada')], default='conta_para_contato', max_length=30, verbose_name='Status no Pipeline'),
        ),
        migrations.RunPython(map_status_forward, reverse_code=map_status_backward),
    ]
