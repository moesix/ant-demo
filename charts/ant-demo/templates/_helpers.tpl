{{- define "ant-demo.labels" -}}
helm.sh/chart: {{ include "ant-demo.chart" . }}
{{ include "ant-demo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "ant-demo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ant-demo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}