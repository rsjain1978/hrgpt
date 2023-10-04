$(document).ready(function() {
    $("#accordion").accordion({
        collapsible: true,
        active: false // Keep it closed initially
    });

    $("#upload-form").submit(function(e) {
        e.preventDefault();
        let file = $("#pdf-upload")[0].files[0];
        let jd = $("#jobdescriptions").val();
        let formData = new FormData();
        formData.append("file", file);
        formData.append("job_description", jd);
        
        $.ajax({
            url: "/upload",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function() {
                // Add spinner
                $("#spinner").show();
            },
            success: function(data) {
                // Remove spinner
                $("#spinner").hide();
                $("#pdf-viewer").attr("src", URL.createObjectURL(file)).show();
                // Call function to display results
                displayAnalysisResults(data);
            },
            error: function() {
                // Also remove spinner in case of error
                $("#spinner").hide();
                alert("An error occurred while uploading the file.");
            }
        });
    });
});


function displayAnalysisResults(data) {
    if(data.success) { 
        $("#accordion").html("<h3>Analysis Result</h3><div>" + data.message + "</div>");
        $("#accordion").accordion("refresh");
        $("#analysis-results").show();
    } else {
        alert("Failed to analyze the resume. Please try again.");
    }
}

